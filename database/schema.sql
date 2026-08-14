-- AquaGuard PostgreSQL + PostGIS Complete Database Schema
-- --------------------------------------------------------
-- Production DDL for water bodies geospatial surveillance, satellite observations,
-- AI/ML predictions, and spatial indexes.

-- 1. Enable PostGIS Spatial Extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- 2. Water Bodies Table
CREATE TABLE IF NOT EXISTS water_bodies (
    id SERIAL PRIMARY KEY,
    water_body_id VARCHAR(64) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    state VARCHAR(100) NOT NULL,
    district VARCHAR(100) NOT NULL,
    geometry TEXT NOT NULL, -- GeoJSON Feature / Polygon Geometry
    area_m2 DOUBLE PRECISION,
    area_hectares DOUBLE PRECISION,
    centroid VARCHAR(100),
    source VARCHAR(100),
    source_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for Water Bodies
CREATE INDEX IF NOT EXISTS idx_water_bodies_wbid ON water_bodies(water_body_id);
CREATE INDEX IF NOT EXISTS idx_water_bodies_state ON water_bodies(state);
CREATE INDEX IF NOT EXISTS idx_water_bodies_district ON water_bodies(district);

-- 3. Observations Table
CREATE TABLE IF NOT EXISTS observations (
    id SERIAL PRIMARY KEY,
    water_body_id VARCHAR(64) NOT NULL REFERENCES water_bodies(water_body_id) ON DELETE CASCADE,
    acquisition_date VARCHAR(50) NOT NULL,
    satellite VARCHAR(100),
    sensor VARCHAR(100),
    source VARCHAR(100) NOT NULL,
    collection_id VARCHAR(100),
    cloud_percentage DOUBLE PRECISION,
    water_area_m2 DOUBLE PRECISION,
    water_area_ha DOUBLE PRECISION,
    mndwi DOUBLE PRECISION,
    ndwi DOUBLE PRECISION,
    ndvi DOUBLE PRECISION,
    rainfall DOUBLE PRECISION,
    data_quality VARCHAR(50),
    processing_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Duplicate Prevention Unique Constraint (Requirement 9)
    CONSTRAINT uq_observation_identity UNIQUE (water_body_id, acquisition_date, source, collection_id)
);

-- Indexes for Observations
CREATE INDEX IF NOT EXISTS idx_obs_wbid ON observations(water_body_id);
CREATE INDEX IF NOT EXISTS idx_obs_acq_date ON observations(acquisition_date);
CREATE INDEX IF NOT EXISTS idx_obs_source ON observations(source);

-- 4. Predictions Table
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    water_body_id VARCHAR(64) NOT NULL REFERENCES water_bodies(water_body_id) ON DELETE CASCADE,
    prediction_date VARCHAR(50) NOT NULL,
    health_class VARCHAR(50) NOT NULL,
    priority VARCHAR(50) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    probability_if_supported DOUBLE PRECISION,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for Predictions
CREATE INDEX IF NOT EXISTS idx_pred_wbid ON predictions(water_body_id);
CREATE INDEX IF NOT EXISTS idx_pred_priority ON predictions(priority);
CREATE INDEX IF NOT EXISTS idx_pred_date ON predictions(prediction_date);

-- 5. Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'viewer',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
