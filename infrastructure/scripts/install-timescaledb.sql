-- Install TimescaleDB extension
-- This must be run by a superuser or a user with CREATE privileges

-- Check if extension is available
SELECT * FROM pg_available_extensions WHERE name = 'timescaledb';

-- Create the TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Verify installation
\dx timescaledb

-- Show TimescaleDB version
SELECT extversion FROM pg_extension WHERE extname = 'timescaledb';
