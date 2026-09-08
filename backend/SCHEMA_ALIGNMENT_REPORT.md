# Schema Alignment Report

## Contract used by this build

This ML Phase 2 build follows the UdyamSetu schema used by:

- `business_reference_profiles_database_ready.csv`
- `database_schema_reference.sql`
- the previously agreed business profile structure containing:
  - `expected_monthly_revenue`
  - `expected_monthly_expenses`
  - `typical_break_even_months`
- the location metrics structure containing:
  - `demand_score`
  - `competition_score`
  - `competition_count`
  - `average_market_price`
  - `opportunity_score`

## Important discrepancy found

A separate combined SQL draft (`udyamsetu_ml_engine_tables.sql`) available during development omitted the three revenue/expense/break-even columns and used different location metric names. That draft cannot directly support the existing 40-profile CSV or the financial recommendation layer.

Therefore, this package intentionally follows the reference schema included here as `database_schema_reference.sql`, which matches the profile CSV and the structure previously supplied to the database team.

## Code changes made for alignment

- `profile_loader.py` reads the complete 14 business-profile data fields used by the ML engine.
- `location_metrics_loader.py` now queries by `location_id`, `business_category`, and optional `subcategory` using the agreed location-metrics columns.
- JSONB requirement/risk fields are normalized safely by `recommendation_engine.py`.
- `decision_engine.result_for_database()` now preserves the original financial, market, and operational inputs instead of writing placeholder values where inputs are available.
- Database confidence is emitted as a numeric value because the database column is numeric.

## Remaining limitation

`average_market_price` is raw price data and cannot honestly be converted into a 0–100 `pricing_score` without a category/location pricing benchmark. The current system therefore uses a neutral pricing score of `50` until a dedicated pricing dataset or model is introduced.
