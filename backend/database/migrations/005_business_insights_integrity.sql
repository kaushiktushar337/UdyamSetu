-- Business Insights integrity constraints.
-- Run after the existing duplicate cleanup. These natural-key indexes prevent
-- future source/date duplicates from being silently multiplied by aggregation.

CREATE UNIQUE INDEX IF NOT EXISTS uq_location_business_metrics_natural_key
ON location_business_metrics (
    location_id,
    LOWER(business_category),
    LOWER(COALESCE(subcategory, '')),
    data_date,
    LOWER(COALESCE(data_source, ''))
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_business_reference_profiles_logical_key
ON business_reference_profiles (
    LOWER(TRIM(business_name)),
    LOWER(TRIM(category)),
    LOWER(TRIM(COALESCE(subcategory, '')))
);
