-- AquaGuard Initial Seed Data Script
-- ------------------------------------
-- Populates PostGIS database with real water body records, GeoJSON geometries,
-- historical observations, and initial predictions.

-- 1. Insert Water Bodies
INSERT INTO water_bodies (water_body_id, name, state, district, geometry, area_m2, area_hectares, centroid, source, source_id)
VALUES
(
    'WB_HYD_001',
    'Hussain Sagar Lake',
    'Telangana',
    'Hyderabad',
    '{"type":"Polygon","coordinates":[[[78.460,17.418],[78.480,17.418],[78.480,17.435],[78.460,17.435],[78.460,17.418]]]}',
    4215300.0,
    421.53,
    '[78.470, 17.4265]',
    'Bhuvan WFS',
    'BHU_TS_HYD_001'
),
(
    'WB_BLR_002',
    'Bellandur Lake',
    'Karnataka',
    'Bengaluru Urban',
    '{"type":"Polygon","coordinates":[[[77.660,12.930],[77.680,12.930],[77.680,12.945],[77.660,12.945],[77.660,12.930]]]}',
    3650000.0,
    365.00,
    '[77.670, 12.9375]',
    'Sentinel-2 GEE',
    'S2_KA_BLR_002'
),
(
    'WB_CHE_003',
    'Chembarambakkam Lake',
    'Tamil Nadu',
    'Kanchipuram',
    '{"type":"Polygon","coordinates":[[[80.010,13.000],[80.040,13.000],[80.040,13.030],[80.010,13.030],[80.010,13.000]]]}',
    15800000.0,
    1580.00,
    '[80.025, 13.0150]',
    'India-WRIS',
    'WRIS_TN_CHE_003'
)
ON CONFLICT (water_body_id) DO UPDATE SET
    name = EXCLUDED.name,
    state = EXCLUDED.state,
    district = EXCLUDED.district,
    geometry = EXCLUDED.geometry,
    area_m2 = EXCLUDED.area_m2,
    area_hectares = EXCLUDED.area_hectares,
    updated_at = CURRENT_TIMESTAMP;

-- 2. Insert Historical Satellite Observations
INSERT INTO observations (water_body_id, acquisition_date, satellite, sensor, source, collection_id, cloud_percentage, water_area_m2, water_area_ha, mndwi, ndwi, ndvi, rainfall, data_quality)
VALUES
('WB_HYD_001', '2024-10-15T05:20:11Z', 'Sentinel-2B', 'MSI', 'Sentinel-2 GEE', 'COPERNICUS/S2_SR_HARMONIZED', 2.14, 4215300.0, 421.53, 0.4285, 0.3120, -0.1542, 12.4, 'EXCELLENT'),
('WB_HYD_001', '2024-09-01T05:18:00Z', 'Landsat-9', 'OLI-2', 'Landsat GEE', 'LANDSAT/LC09/C02/T1_L2', 1.05, 4240000.0, 424.00, 0.4350, 0.3200, -0.1500, 11.2, 'EXCELLENT'),
('WB_BLR_002', '2024-10-12T05:22:00Z', 'Sentinel-2A', 'MSI', 'Sentinel-2 GEE', 'COPERNICUS/S2_SR_HARMONIZED', 5.80, 3650000.0, 365.00, 0.1850, 0.1200, 0.3450, 8.5, 'GOOD'),
('WB_CHE_003', '2024-10-10T05:15:00Z', 'Sentinel-2B', 'MSI', 'Sentinel-2 GEE', 'COPERNICUS/S2_SR_HARMONIZED', 0.50, 15800000.0, 1580.00, 0.3850, 0.2950, -0.0850, 24.2, 'EXCELLENT')
ON CONFLICT ON CONSTRAINT uq_observation_identity DO NOTHING;

-- 3. Insert Initial ML Predictions
INSERT INTO predictions (water_body_id, prediction_date, health_class, priority, model_version, probability_if_supported)
VALUES
('WB_HYD_001', '2026-08-14', 'GOOD', 'LOW', '1.0.0', 0.2136),
('WB_BLR_002', '2026-08-14', 'CRITICAL', 'CRITICAL', '1.0.0', 0.8950),
('WB_CHE_003', '2026-08-14', 'HIGH_RISK', 'HIGH', '1.0.0', 0.7420);
