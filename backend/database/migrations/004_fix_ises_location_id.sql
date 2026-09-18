BEGIN;

-- Existing UdyamSetu deployments may use integer or UUID location IDs.
-- Store the ISES foreign reference as text so both deployments work without
-- changing the existing location tables.
ALTER TABLE IF EXISTS ises_city_sector_metrics
    ALTER COLUMN location_id TYPE TEXT
    USING location_id::TEXT;

COMMIT;
