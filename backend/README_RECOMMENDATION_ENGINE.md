
# Recommendation / Score Generation Layer

New modules:

- `ml_engine/recommendation_engine.py`
- `ml_engine/location_metrics_loader.py`
- `ml_engine/recommendation_pipeline.py`

Flow:

`UserBusinessContext → BusinessMatcher → Top profiles → RecommendationEngine → Generated engine inputs`

The layer is intentionally transparent. It does not fabricate missing business data. Missing financial fields are recorded as data gaps, and location market data uses neutral fallback scores until the `location_business_metrics` schema/data is fully connected.

Run:

```bash
python recommendation_demo.py
```
