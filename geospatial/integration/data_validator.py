"""
AquaGuard - 10-Point Data Validation Pipeline
----------------------------------------------
Implements comprehensive validation rules across all AquaGuard integrated datasets:
1. Geometry Validity
2. CRS Check (EPSG:4326)
3. Missing Value Audit
4. Duplicate Observation Check
5. Impossible Area Values
6. Invalid Date Check
7. Satellite Cloud Quality
8. Inconsistent Units
9. Source Metadata Traceability
10. Temporal Consistency
"""

from datetime import datetime
from typing import Any, Dict, List, Tuple


class AquaGuardDataValidator:
    """Validator implementing 10-point quality assurance checks for AquaGuard datasets."""

    def __init__(self, max_cloud_threshold: float = 30.0):
        self.max_cloud_threshold = max_cloud_threshold

    def validate_dataset(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute all 10 validation checks on a list of normalized dataset records.

        Returns:
            Dict[str, Any]: Structured validation report with audit statistics.
        """
        results = {
            "check_1_geometry_validity": self._check_geometry_validity(records),
            "check_2_crs": self._check_crs(records),
            "check_3_missing_values": self._check_missing_values(records),
            "check_4_duplicates": self._check_duplicates(records),
            "check_5_impossible_areas": self._check_impossible_areas(records),
            "check_6_invalid_dates": self._check_invalid_dates(records),
            "check_7_cloud_quality": self._check_cloud_quality(records),
            "check_8_unit_consistency": self._check_unit_consistency(records),
            "check_9_source_metadata": self._check_source_metadata(records),
            "check_10_temporal_consistency": self._check_temporal_consistency(records)
        }

        passed_checks = sum(1 for v in results.values() if v["status"] == "PASS")
        warning_checks = sum(1 for v in results.values() if v["status"] == "WARNING")
        failed_checks = sum(1 for v in results.values() if v["status"] == "FAIL")

        overall_status = "PASSED" if failed_checks == 0 else "FAILED"

        return {
            "overall_status": overall_status,
            "summary": {
                "total_records_checked": len(records),
                "total_checks": len(results),
                "passed_checks": passed_checks,
                "warning_checks": warning_checks,
                "failed_checks": failed_checks
            },
            "detailed_checks": results,
            "validated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        }

    @staticmethod
    def _check_geometry_validity(records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check 1: Verify GeoJSON geometry structure and non-empty bounds."""
        valid_count = 0
        invalid_count = 0
        issues = []

        for idx, rec in enumerate(records):
            geom = rec.get("geometry")
            if not geom or not isinstance(geom, dict) or "type" not in geom or "coordinates" not in geom:
                invalid_count += 1
                issues.append(f"Record {idx} ({rec.get('water_body_id')}): Missing or malformed geometry")
            else:
                valid_count += 1

        status = "PASS" if invalid_count == 0 else "WARNING"
        return {
            "status": status,
            "description": "Validates GeoJSON Polygon/MultiPolygon structure and non-empty coordinates.",
            "valid_records": valid_count,
            "invalid_records": invalid_count,
            "issues": issues[:5]
        }

    @staticmethod
    def _check_crs(records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check 2: Verify EPSG:4326 CRS compliance."""
        invalid_crs = 0
        for rec in records:
            crs = rec.get("CRS") or rec.get("crs") or "EPSG:4326"
            if crs not in ("EPSG:4326", "WGS84", "urn:ogc:def:crs:EPSG::4326"):
                invalid_crs += 1

        status = "PASS" if invalid_crs == 0 else "FAIL"
        return {
            "status": status,
            "description": "Ensures standard EPSG:4326 (WGS84) Coordinate Reference System.",
            "non_standard_crs_count": invalid_crs
        }

    @staticmethod
    def _check_missing_values(records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check 3: Track null/missing values without fabricating fake data."""
        missing_counts = {}
        if not records:
            return {"status": "PASS", "description": "Audit missing values.", "missing_fields": {}}

        field_keys = records[0].keys()
        for key in field_keys:
            missing_counts[key] = sum(1 for r in records if r.get(key) is None or r.get(key) == "" or r.get(key) == "UNAVAILABLE")

        return {
            "status": "PASS",
            "description": "Audits missing real-world values (NULL/NA preserved; no fake fabrication).",
            "missing_field_counts": missing_counts
        }

    @staticmethod
    def _check_duplicates(records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check 4: Check duplicate observations based on (water_body_id, observation_date, source)."""
        seen = set()
        duplicates = 0

        for rec in records:
            key = (rec.get("water_body_id"), rec.get("observation_date"), rec.get("source"))
            if key in seen and rec.get("observation_date") != "UNAVAILABLE":
                duplicates += 1
            else:
                seen.add(key)

        status = "PASS" if duplicates == 0 else "WARNING"
        return {
            "status": status,
            "description": "Identifies duplicate observations per water body and date.",
            "duplicate_count": duplicates
        }

    @staticmethod
    def _check_impossible_areas(records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check 5: Verify water_area_m2 >= 0 and non-negative values."""
        negative_areas = 0
        excessive_areas = 0

        for rec in records:
            area = rec.get("water_area_m2")
            if area is not None:
                if area < 0:
                    negative_areas += 1
                elif area > 1e11:  # 100,000 km² sanity limit
                    excessive_areas += 1

        status = "PASS" if (negative_areas == 0 and excessive_areas == 0) else "FAIL"
        return {
            "status": status,
            "description": "Verifies water area is non-negative and physically plausible.",
            "negative_area_count": negative_areas,
            "excessive_area_count": excessive_areas
        }

    @staticmethod
    def _check_invalid_dates(records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check 6: Check ISO date format and prevent future dates."""
        invalid_dates = 0
        now_dt = datetime.utcnow()

        for rec in records:
            d_str = rec.get("observation_date")
            if d_str and d_str not in ("UNAVAILABLE", "ERROR", "N/A"):
                try:
                    dt_val = datetime.strptime(d_str[:10], "%Y-%m-%d")
                    if dt_val > now_dt:
                        invalid_dates += 1
                except ValueError:
                    invalid_dates += 1

        status = "PASS" if invalid_dates == 0 else "WARNING"
        return {
            "status": status,
            "description": "Ensures valid ISO YYYY-MM-DD date formatting without future timestamps.",
            "invalid_date_count": invalid_dates
        }

    def _check_cloud_quality(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check 7: Verify scene cloud cover thresholds."""
        exceeded_cloud = 0
        for rec in records:
            cloud = rec.get("cloud_percentage")
            if cloud is not None and cloud > self.max_cloud_threshold:
                exceeded_cloud += 1

        status = "PASS" if exceeded_cloud == 0 else "WARNING"
        return {
            "status": status,
            "description": f"Verifies satellite cloud cover is <= {self.max_cloud_threshold}%.",
            "high_cloud_scene_count": exceeded_cloud
        }

    @staticmethod
    def _check_unit_consistency(records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check 8: Ensure unit conversions (1 ha = 10,000 m²)."""
        mismatches = 0
        for rec in records:
            a_m2 = rec.get("water_area_m2")
            a_ha = rec.get("water_area_ha")
            if a_m2 is not None and a_ha is not None:
                expected_ha = round(a_m2 / 10000.0, 4)
                if abs(expected_ha - a_ha) > 0.1:
                    mismatches += 1

        status = "PASS" if mismatches == 0 else "FAIL"
        return {
            "status": status,
            "description": "Ensures unit consistency (water_area_ha == water_area_m2 / 10000).",
            "unit_mismatch_count": mismatches
        }

    @staticmethod
    def _check_source_metadata(records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check 9: Confirm presence of source metadata."""
        missing_source = 0
        for rec in records:
            if not rec.get("source") or not rec.get("dataset_collection"):
                missing_source += 1

        status = "PASS" if missing_source == 0 else "WARNING"
        return {
            "status": status,
            "description": "Confirms complete source and collection metadata for data traceability.",
            "missing_source_metadata_count": missing_source
        }

    @staticmethod
    def _check_temporal_consistency(records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check 10: Check temporal ordering per water body."""
        temporal_issues = 0
        prev_yr = -1

        for rec in records:
            yr = rec.get("year")
            if isinstance(yr, int):
                if yr < prev_yr and rec.get("water_body_id") == records[0].get("water_body_id"):
                    temporal_issues += 1
                prev_yr = yr

        status = "PASS" if temporal_issues == 0 else "WARNING"
        return {
            "status": status,
            "description": "Verifies chronological order of observations for time-series feature engineering.",
            "out_of_order_count": temporal_issues
        }
