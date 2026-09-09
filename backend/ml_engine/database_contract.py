"""Database contract used by integration tests and payload validation.

This contract matches the ML schema previously provided to the database team,
including the revenue/expense/break-even fields used by the 40-profile dataset.
"""
from __future__ import annotations

REFERENCE_PROFILE_COLUMNS = {
    "profile_id", "business_name", "category", "subcategory",
    "minimum_capital", "typical_project_cost", "expected_monthly_revenue",
    "expected_monthly_expenses", "expected_profit_margin",
    "typical_break_even_months", "resource_requirements",
    "infrastructure_requirements", "risk_factors", "data_source",
    "created_at", "updated_at",
}

LOCATION_METRIC_COLUMNS = {
    "metric_id", "location_id", "business_category", "subcategory",
    "demand_score", "competition_count", "competition_score",
    "average_market_price", "opportunity_score", "data_source", "data_date",
    "created_at", "updated_at",
}

WRITE_TABLE_REQUIRED_COLUMNS = {
    "business_analyses": {"overall_score", "decision", "confidence", "analysis_status"},
    "analysis_scores": {"market_score", "operational_score", "financial_score", "risk_score", "overall_score"},
    "market_analyses": {"demand_score", "competition_score", "market_gap_score", "pricing_score", "opportunity_score"},
    "operational_analyses": {"resource_score", "infrastructure_score", "supply_chain_score", "logistics_score", "operational_score"},
    "financial_analyses": {"estimated_project_cost", "available_capital", "funding_gap", "estimated_monthly_revenue", "estimated_monthly_expenses", "estimated_monthly_profit", "break_even_months"},
    "analysis_risks": set(),
    "analysis_recommendations": set(),
}
