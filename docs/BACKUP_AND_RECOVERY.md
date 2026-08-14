# AquaGuard Backup and Recovery Strategy

This document outlines the backup, restoration, and disaster recovery procedures for the **AquaGuard** surveillance platform.

---

## 1. Database Backup & Restoration

### PostgreSQL + PostGIS Automated Dump

To create an automated database backup of all water bodies, observations, predictions, and PostGIS spatial geometries:

```bash
# Export full PostGIS database dump
docker exec -t aquaguard_postgres pg_dump -U postgres -d aquaguard_db --clean --if-exists > aquaguard_db_backup_$(date +%Y%m%d_%H%M%S).sql
```

### Database Restoration

To restore from a backup SQL file:

```bash
# Restore database snapshot
cat aquaguard_db_backup_YYYYMMDD_HHMMSS.sql | docker exec -i aquaguard_postgres psql -U postgres -d aquaguard_db
```

---

## 2. Raw & Processed Data Persistence

1. **Raw Satellite Imagery & GIS Vectors**:
   - Location: `data/raw/`
   - Strategy: Synchronized to cloud storage (e.g. AWS S3 / Google Cloud Storage) nightly.
2. **Processed Features & Predictions**:
   - Location: `data/datasets/` & `data/processed/`
   - Strategy: Versioned via Git LFS / cloud bucket snapshots.

---

## 3. AI/ML Model Artifact Backup

Model files stored in `models/` (`restoration_priority_model.pkl`, `scaler.pkl`, `model_metadata.json`) are preserved in version control and backed up alongside release tags.

---

## 4. Emergency Disaster Recovery RTO/RPO

- **Recovery Time Objective (RTO)**: < 15 minutes (via `docker compose up -d`).
- **Recovery Point Objective (RPO)**: < 24 hours (nightly automated DB dumps).
