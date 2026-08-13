-- Z1 Carbon Footprint Connector
-- Normalized PostgreSQL storage for Google Cloud Carbon Footprint exports.

CREATE TABLE IF NOT EXISTS z1_carbon_footprint (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usage_month DATE NOT NULL,
    billing_account_id TEXT NOT NULL,
    project_id TEXT,
    project_number TEXT,
    project_name TEXT,
    service_id TEXT,
    service_description TEXT,
    region TEXT,
    scope1_kgco2e NUMERIC(24,9) NOT NULL DEFAULT 0,
    scope2_market_based_kgco2e NUMERIC(24,9) NOT NULL DEFAULT 0,
    scope2_location_based_kgco2e NUMERIC(24,9) NOT NULL DEFAULT 0,
    scope3_kgco2e NUMERIC(24,9) NOT NULL DEFAULT 0,
    total_location_based_kgco2e NUMERIC(24,9) NOT NULL DEFAULT 0,
    total_market_based_kgco2e NUMERIC(24,9) NOT NULL DEFAULT 0,
    total_after_offsets_kgco2e NUMERIC(24,9) NOT NULL DEFAULT 0,
    source_dataset TEXT NOT NULL,
    source_table TEXT NOT NULL,
    source_row_hash TEXT NOT NULL,
    imported_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    raw_payload JSONB,
    UNIQUE (source_row_hash)
);

CREATE INDEX IF NOT EXISTS idx_z1_carbon_usage_month
    ON z1_carbon_footprint (usage_month);
CREATE INDEX IF NOT EXISTS idx_z1_carbon_project_month
    ON z1_carbon_footprint (project_id, usage_month);
CREATE INDEX IF NOT EXISTS idx_z1_carbon_service_month
    ON z1_carbon_footprint (service_description, usage_month);
CREATE INDEX IF NOT EXISTS idx_z1_carbon_region_month
    ON z1_carbon_footprint (region, usage_month);

CREATE OR REPLACE VIEW z1_carbon_monthly AS
SELECT
    usage_month,
    SUM(scope1_kgco2e) AS scope1_kgco2e,
    SUM(scope2_market_based_kgco2e) AS scope2_market_based_kgco2e,
    SUM(scope2_location_based_kgco2e) AS scope2_location_based_kgco2e,
    SUM(scope3_kgco2e) AS scope3_kgco2e,
    SUM(total_location_based_kgco2e) AS total_location_based_kgco2e,
    SUM(total_market_based_kgco2e) AS total_market_based_kgco2e,
    SUM(total_after_offsets_kgco2e) AS total_after_offsets_kgco2e
FROM z1_carbon_footprint
GROUP BY usage_month;
