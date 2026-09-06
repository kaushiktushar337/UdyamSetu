# UdyamSetu Decision Engine — Complete Prototype

## Implemented modules
- Financial Feasibility Engine
- Market Feasibility Engine
- Operational Feasibility Engine
- Risk Engine
- Final Decision Engine
- Database mapping layer

## Database scheme alignment

### Reference/read data
- `business_reference_profiles`
- `location_business_metrics`

### Analysis/write data
- `business_analyses`
- `analysis_scores`
- `market_analyses`
- `operational_analyses`
- `financial_analyses`
- `analysis_risks`
- `analysis_recommendations`

The engine currently works independently with structured inputs. Database/API integration can be added without changing the core scoring modules.

## Run the complete prototype

```bash
python complete_demo.py
```

## Current decision labels
- 80–100: Highly Viable
- 65–79: Viable
- 45–64: Needs Modification
- Below 45: Reconsider

## Important
This is an explainable rule-based v1 engine. Scoring weights and thresholds are centralized in modules so they can later be calibrated from real business and market data.
