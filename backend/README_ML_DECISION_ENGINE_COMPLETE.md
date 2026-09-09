# UdyamSetu ML Decision Engine — Complete Backend Layer

## Runtime flow

User business context
→ semantic business matcher (MiniLM, 384 dimensions)
→ `business_reference_profiles`
→ optional `location_business_metrics`
→ financial + market + operational + risk engines
→ optional Ridge calibration model
→ ranked recommendations
→ selected result mapped to the agreed database schema
→ transactional persistence to analysis tables.

## Database alignment

Reads:
- `business_reference_profiles`
- `location_business_metrics`

Writes only to the agreed tables:
- `business_analyses`
- `analysis_scores`
- `market_analyses`
- `operational_analyses`
- `financial_analyses`
- `analysis_risks`
- `analysis_recommendations`

`business_id` is never substituted with `profile_id`. `business_id` remains the ID from the existing application business table, as required by the database schema.

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Offline demo

```bash
python ml_decision_demo.py
```

## Live database usage

```python
from ml_engine.decision_service import UdyamSetuDecisionService
from ml_engine.recommendation_engine import UserBusinessContext

service = UdyamSetuDecisionService.from_database()
results = service.recommend(UserBusinessContext(
    available_capital=300000,
    interests="bakery food processing",
    skills="bakery and business management",
    location_id="YOUR_LOCATION_UUID",
))
```

Persist only after a recommendation is selected and a valid existing `business_id` is available.
