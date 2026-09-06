"""Database integration contract for the 9-table ML schema agreed with the database team.

Read/reference tables:
1. business_reference_profiles
2. location_business_metrics

Write/result tables:
3. business_analyses
4. analysis_scores
5. market_analyses
6. operational_analyses
7. financial_analyses
8. analysis_risks
9. analysis_recommendations
"""

from .decision_engine import result_for_database

def map_analysis_result(result):
    return result_for_database(result)
