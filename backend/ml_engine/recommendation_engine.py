"""Bridge between matched business profiles and the existing decision engines."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .profile_loader import BusinessProfile
from .business_matcher import BusinessMatch
from .schemas import FinancialInput
from .market_engine import MarketInput
from .operational_engine import OperationalInput
from .risk_engine import RiskItem


@dataclass
class UserBusinessContext:
    available_capital: float
    funding_available: float = 0.0
    interests: str = ""
    skills: str = ""
    experience_years: float = 0.0
    available_resources: List[str] = field(default_factory=list)
    infrastructure: List[str] = field(default_factory=list)
    location: Optional[str] = None
    location_id: Optional[str] = None
    preferences: str = ""


@dataclass
class GeneratedInputs:
    financial: FinancialInput
    market: MarketInput
    operational: OperationalInput
    business_risks: List[RiskItem]
    explanation: Dict[str, Any]


def _text(value: Any) -> str:
    """Normalize TEXT/JSONB/list values returned by PostgreSQL into text."""
    if value is None:
        return ""
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.startswith("[") or stripped.startswith("{"):
            try:
                return _text(json.loads(stripped))
            except (ValueError, TypeError):
                return value
        return value
    if isinstance(value, dict):
        return " ".join(f"{k} {v}" for k, v in value.items())
    if isinstance(value, (list, tuple, set)):
        return " ".join(_text(v) for v in value)
    return str(value)


class RecommendationEngine:
    @staticmethod
    def _clamp(value: Any) -> float:
        try:
            return max(0.0, min(100.0, float(value)))
        except (TypeError, ValueError):
            return 50.0

    @staticmethod
    def _keyword_overlap(requirements: Any, user_assets: str, neutral: float = 50.0) -> float:
        words = [
            word.strip(".,;:()[]{}\"'").lower()
            for word in _text(requirements).replace("/", " ").replace("-", " ").split()
        ]
        unique = list(dict.fromkeys(word for word in words if len(word) > 4))[:40]
        if not unique:
            return neutral
        assets = user_assets.lower()
        matches = sum(1 for word in unique if word in assets)
        return round(max(20.0, min(100.0, 20.0 + 80.0 * matches / len(unique))), 2)

    def generate_financial_input(self, context: UserBusinessContext, profile: BusinessProfile) -> FinancialInput:
        project_cost = profile.typical_project_cost or profile.minimum_capital or context.available_capital
        revenue = profile.expected_monthly_revenue or 0.0
        expenses = profile.expected_monthly_expenses
        if expenses is None and revenue > 0 and profile.expected_profit_margin is not None:
            expenses = revenue * (1 - float(profile.expected_profit_margin) / 100.0)
        if expenses is None:
            expenses = 0.0
        return FinancialInput(
            available_capital=float(context.available_capital),
            funding_available=float(context.funding_available),
            estimated_project_cost=float(project_cost),
            estimated_monthly_revenue=float(revenue),
            estimated_monthly_expenses=float(expenses),
        )

    def generate_market_input(self, location_metrics: Optional[Dict[str, Any]], semantic_score: Optional[float]) -> MarketInput:
        metrics = location_metrics or {}
        demand = metrics.get("demand_score", semantic_score if semantic_score is not None else 50.0)
        competition = metrics.get("competition_score", 50.0)
        opportunity = metrics.get("opportunity_score", 50.0)
        # The agreed database schema stores average_market_price, not pricing_score.
        # A neutral pricing score is retained until a pricing-potential model/data source exists.
        pricing = metrics.get("pricing_score", 50.0)
        return MarketInput(
            demand_score=self._clamp(demand),
            competition_score=self._clamp(competition),
            opportunity_score=self._clamp(opportunity),
            pricing_score=self._clamp(pricing),
        )

    def generate_operational_input(self, context: UserBusinessContext, profile: BusinessProfile) -> OperationalInput:
        assets = " ".join(context.available_resources + context.infrastructure + [context.skills])
        resource_score = self._keyword_overlap(profile.resource_requirements, assets)
        infrastructure_score = self._keyword_overlap(
            profile.infrastructure_requirements,
            " ".join(context.infrastructure + context.available_resources),
        )
        experience_score = self._clamp(35.0 + context.experience_years * 12.0)
        lower = assets.lower()
        supply_chain_score = max(experience_score, 70.0) if any(x in lower for x in ["supplier", "vendor", "supply"]) else experience_score
        logistics_score = max(experience_score, 70.0) if any(x in lower for x in ["transport", "delivery", "vehicle", "logistics", "distribution"]) else experience_score
        return OperationalInput(
            resource_score=round(resource_score, 2),
            infrastructure_score=round(infrastructure_score, 2),
            supply_chain_score=round(self._clamp(supply_chain_score), 2),
            logistics_score=round(self._clamp(logistics_score), 2),
        )

    def generate_business_risks(self, context: UserBusinessContext, profile: BusinessProfile, market_input: MarketInput) -> List[RiskItem]:
        risks: List[RiskItem] = []
        risk_text = _text(profile.risk_factors).strip()
        if risk_text:
            factor_count = len([part for part in risk_text.replace(";", ",").split(",") if part.strip()])
            risks.append(RiskItem(
                risk_type="Business",
                risk_score=self._clamp(25 + factor_count * 8),
                description=risk_text,
                mitigation="Review the documented business risks and prepare practical mitigation measures before scaling.",
            ))
        required = profile.typical_project_cost or profile.minimum_capital
        if required and context.available_capital + context.funding_available < float(required):
            risks.append(RiskItem("Capital Gap", 70.0,
                "Available capital and declared funding do not cover the reference project cost.",
                "Reduce initial scale, phase investment, or arrange suitable funding."))
        if market_input.competition_score >= 70:
            risks.append(RiskItem("Competition", float(market_input.competition_score),
                "The location metrics indicate high competitive pressure.",
                "Differentiate through pricing, quality, service, niche targeting, or location."))
        return risks

    def generate_inputs(self, context: UserBusinessContext, match: BusinessMatch, location_metrics: Optional[Dict[str, Any]] = None) -> GeneratedInputs:
        profile = match.profile
        financial = self.generate_financial_input(context, profile)
        market = self.generate_market_input(location_metrics, match.semantic_score)
        operational = self.generate_operational_input(context, profile)
        business_risks = self.generate_business_risks(context, profile, market)
        data_gaps = [name for name, value in {
            "minimum_capital": profile.minimum_capital,
            "typical_project_cost": profile.typical_project_cost,
            "expected_monthly_revenue": profile.expected_monthly_revenue,
            "expected_monthly_expenses": profile.expected_monthly_expenses,
            "expected_profit_margin": profile.expected_profit_margin,
            "typical_break_even_months": profile.typical_break_even_months,
        }.items() if value is None]
        return GeneratedInputs(
            financial=financial,
            market=market,
            operational=operational,
            business_risks=business_risks,
            explanation={
                "business": profile.business_name,
                "match_score": match.final_score,
                "semantic_score": match.semantic_score,
                "capital_match_score": match.capital_score,
                "market_data_available": bool(location_metrics),
                "data_gaps": data_gaps,
            },
        )
