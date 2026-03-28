-- Initialize Sevai Hub database with PostGIS extension
-- This file is run automatically when the database container starts

-- Create PostGIS extension (if not already exists)
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Confirm extensions are installed
SELECT postgis_version();
