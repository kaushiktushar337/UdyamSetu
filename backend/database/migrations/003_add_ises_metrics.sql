BEGIN;

CREATE TABLE IF NOT EXISTS ises_city_sector_metrics (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    location_id TEXT NOT NULL,

    city VARCHAR(100) NOT NULL,

    sector VARCHAR(30) NOT NULL
        CHECK (sector IN ('Production', 'Retail', 'Other Services')),

    weighted_businesses NUMERIC(15,2),

    avg_regular_month_sales NUMERIC(15,2),

    profit_business_pct NUMERIC(6,2),

    avg_workers NUMERIC(8,2),

    paid_worker_pct NUMERIC(6,2),

    bank_account_pct NUMERIC(6,2),

    business_loan_pct NUMERIC(6,2),

    loan_application_pct NUMERIC(6,2),

    competitor_monitoring_pct NUMERIC(6,2),

    customer_feedback_pct NUMERIC(6,2),

    supplier_market_info_pct NUMERIC(6,2),

    monthly_budget_pct NUMERIC(6,2),

    sales_target_pct NUMERIC(6,2),

    electricity_use_pct NUMERIC(6,2),

    electricity_grid_pct NUMERIC(6,2),

    power_outage_pct NUMERIC(6,2),

    water_use_pct NUMERIC(6,2),

    computer_use_pct NUMERIC(6,2),

    smartphone_use_pct NUMERIC(6,2),

    contractual_input_purchase_pct NUMERIC(6,2),

    informal_payment_pct NUMERIC(6,2),

    data_source TEXT NOT NULL,

    data_date DATE NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(location_id, sector, data_date)
);


-- Keep the ISES table compatible with the existing UdyamSetu location IDs.
-- Some deployments use integer location IDs while older schema files used UUIDs.
ALTER TABLE ises_city_sector_metrics
    ALTER COLUMN location_id TYPE TEXT
    USING location_id::TEXT;


CREATE INDEX IF NOT EXISTS
idx_ises_city_sector_location
ON ises_city_sector_metrics(location_id);

CREATE INDEX IF NOT EXISTS
idx_ises_city_sector_sector
ON ises_city_sector_metrics(sector);

COMMIT;