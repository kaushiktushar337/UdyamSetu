"""Confidence estimation for the explainable decision engine.

This is intentionally a data-quality/confidence estimate, not a probability that
an investment will succeed. The database stores it as NUMERIC(5,4).
"""
from __future__ import annotations


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def estimate_confidence(profile, generated, calibration=None, asuse_prediction=None) -> float:
    fields = (
        "minimum_capital", "typical_project_cost", "expected_monthly_revenue",
        "expected_monthly_expenses", "expected_profit_margin",
        "typical_break_even_months", "resource_requirements",
        "infrastructure_requirements", "risk_factors", "data_source",
    )
    present = sum(1 for field in fields if getattr(profile, field, None) not in (None, "", [], {}))
    profile_quality = present / len(fields)
    location_quality = 1.0 if generated.explanation.get("market_data_available") else 0.55
    calibrated = 1.0 if calibration is not None and getattr(calibration, "model_used", False) else 0.75
    asuse_quality = 1.0 if asuse_prediction is not None and getattr(asuse_prediction, "model_used", False) else 0.70

    # Profile evidence is strongest; location and model evidence are secondary.
    score = profile_quality * 0.50 + location_quality * 0.25 + calibrated * 0.10 + asuse_quality * 0.15
    return round(clamp01(score), 4)
