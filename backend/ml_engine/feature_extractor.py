"""Feature extraction contract for UdyamSetu's learnable calibration layer.

The extractor turns one recommendation into a stable numeric feature vector.
It deliberately uses values already produced by the existing matcher and
explainable decision engines; it does not replace those engines.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict

FEATURE_SCHEMA_VERSION = "1.0"

FEATURE_NAMES = (
    "semantic_match_score",
    "capital_match_score",
    "available_capital",
    "funding_available",
    "capital_to_cost_ratio",
    "estimated_project_cost",
    "expected_monthly_revenue",
    "expected_monthly_expenses",
    "expected_profit_margin",
    "typical_break_even_months",
    "demand_score",
    "competition_score",
    "opportunity_score",
    "pricing_score",
    "resource_score",
    "infrastructure_score",
    "supply_chain_score",
    "logistics_score",
    "financial_score",
    "market_score",
    "operational_score",
    "risk_feasibility_score",
    "profile_data_completeness",
    "location_data_available",
)


@dataclass(frozen=True)
class FeatureVector:
    schema_version: str
    values: Dict[str, float]

    def as_dict(self) -> Dict[str, Any]:
        return {"schema_version": self.schema_version, "features": dict(self.values)}

    def ordered(self) -> list[float]:
        return [float(self.values[name]) for name in FEATURE_NAMES]


def _num(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: Any) -> float:
    return max(0.0, min(100.0, _num(value)))


def _profile_completeness(profile) -> float:
    fields = (
        "minimum_capital", "typical_project_cost", "expected_monthly_revenue",
        "expected_monthly_expenses", "expected_profit_margin",
        "typical_break_even_months", "resource_requirements",
        "infrastructure_requirements", "risk_factors", "data_source",
    )
    present = sum(1 for field in fields if getattr(profile, field, None) not in (None, "", [], {}))
    return round(present / len(fields) * 100.0, 2)


class FeatureExtractor:
    """Build the versioned feature vector used by the calibration model."""

    def extract(self, context, match, generated, analysis) -> FeatureVector:
        profile = match.profile
        financial = generated.financial
        market = generated.market
        operational = generated.operational

        project_cost = _num(financial.estimated_project_cost)
        total_capital = _num(context.available_capital) + _num(context.funding_available)
        capital_ratio = total_capital / project_cost if project_cost > 0 else 1.0

        values = {
            "semantic_match_score": _clamp(match.semantic_score),
            "capital_match_score": _clamp(match.capital_score),
            "available_capital": _num(context.available_capital),
            "funding_available": _num(context.funding_available),
            "capital_to_cost_ratio": max(0.0, capital_ratio),
            "estimated_project_cost": project_cost,
            "expected_monthly_revenue": _num(getattr(profile, "expected_monthly_revenue", None)),
            "expected_monthly_expenses": _num(getattr(profile, "expected_monthly_expenses", None)),
            "expected_profit_margin": _num(getattr(profile, "expected_profit_margin", None)),
            "typical_break_even_months": _num(getattr(profile, "typical_break_even_months", None)),
            "demand_score": _clamp(market.demand_score),
            "competition_score": _clamp(market.competition_score),
            "opportunity_score": _clamp(market.opportunity_score),
            "pricing_score": _clamp(market.pricing_score),
            "resource_score": _clamp(operational.resource_score),
            "infrastructure_score": _clamp(operational.infrastructure_score),
            "supply_chain_score": _clamp(operational.supply_chain_score),
            "logistics_score": _clamp(operational.logistics_score),
            "financial_score": _clamp(analysis.financial.financial_score),
            "market_score": _clamp(analysis.market.market_score),
            "operational_score": _clamp(analysis.operational.operational_score),
            "risk_feasibility_score": _clamp(analysis.risk.feasibility_risk_score),
            "profile_data_completeness": _profile_completeness(profile),
            "location_data_available": 100.0 if generated.explanation.get("market_data_available") else 0.0,
        }
        return FeatureVector(FEATURE_SCHEMA_VERSION, values)
