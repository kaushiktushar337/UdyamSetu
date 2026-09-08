# UdyamSetu ML Phase 2 — Feature & Calibration Layer

## What was added

- `ml_engine/feature_extractor.py` — versioned numeric feature contract.
- `ml_engine/calibration_model.py` — small optional Ridge calibration model.
- `ml_engine/database_contract.py` — database-column contract used by tests.
- `tests/test_ml_phase2.py` — schema and end-to-end integration tests.
- `database_schema_reference.sql` — agreed reference schema used for alignment checks.

## Runtime flow

`User context → semantic matcher → business profile → recommendation input generation → existing decision engines → feature extraction → optional calibration → ranked result`

## Important behavior

The calibration model is **disabled by default**. Until it is trained on at least 20 labelled real outcomes, the final recommendation score remains the explainable Decision Engine score.

This prevents the system from pretending that 40 business reference profiles are sufficient supervised training data.

## Database alignment

The read contract is:

- `business_reference_profiles` with revenue, expenses and break-even columns used by the 40-profile CSV.
- `location_business_metrics` with `demand_score`, `competition_score`, `competition_count`, `average_market_price`, and `opportunity_score`.

The pricing-potential score is **not currently present in the agreed location table**, so it remains neutral (`50`) until a proper pricing dataset/model is added.

## Test

```bash
python -m unittest discover -s tests -v
```
