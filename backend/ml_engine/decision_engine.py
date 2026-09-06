from dataclasses import dataclass, asdict
from typing import List, Optional

from .schemas import FinancialInput
from .financial_engine import calculate_financial_feasibility
from .market_engine import MarketInput, calculate_market_feasibility
from .operational_engine import OperationalInput, calculate_operational_feasibility
from .risk_engine import RiskInput, RiskItem, calculate_risk

@dataclass
class BusinessAnalysisInput:
    financial: FinancialInput
    market: MarketInput
    operational: OperationalInput
    business_risks: List[RiskItem]

@dataclass
class BusinessAnalysisResult:
    overall_score: float
    decision: str
    confidence: str
    financial: object
    market: object
    operational: object
    risk: object
    recommendations: List[str]

DEFAULT_FINAL_WEIGHTS = {
    "financial": 0.30,
    "market": 0.30,
    "operational": 0.20,
    "risk": 0.20,
}

def calculate_business_analysis(data: BusinessAnalysisInput, weights=None):
    weights = weights or DEFAULT_FINAL_WEIGHTS

    financial = calculate_financial_feasibility(data.financial)
    market = calculate_market_feasibility(data.market)
    operational = calculate_operational_feasibility(data.operational)

    risk = calculate_risk(RiskInput(
        capital_coverage_ratio=financial.capital_coverage_ratio,
        competition_score=data.market.competition_score,
        operational_score=operational.operational_score,
        business_risks=data.business_risks,
    ))

    overall = round(
        financial.financial_score * weights["financial"] +
        market.market_score * weights["market"] +
        operational.operational_score * weights["operational"] +
        risk.feasibility_risk_score * weights["risk"],
        2
    )

    if overall >= 80:
        decision = "Highly Viable"
    elif overall >= 65:
        decision = "Viable"
    elif overall >= 45:
        decision = "Needs Modification"
    else:
        decision = "Reconsider"

    # Confidence is deliberately based on completeness/consistency of supplied scores,
    # not a statistical probability claim.
    confidence = "Prototype / rule-based"

    recommendations = []
    recommendations.extend(financial.recommendations)
    recommendations.extend(market.recommendations)
    recommendations.extend(operational.recommendations)

    if risk.severity == "High":
        recommendations.append("Address high-severity risks before committing to full-scale investment.")

    # Remove duplicates while preserving order.
    recommendations = list(dict.fromkeys(recommendations))

    return BusinessAnalysisResult(
        overall_score=overall,
        decision=decision,
        confidence=confidence,
        financial=financial,
        market=market,
        operational=operational,
        risk=risk,
        recommendations=recommendations,
    )

def result_for_database(result):
    """Maps engine output to the database team's agreed ML table scheme."""
    return {
        "business_analyses": {
            "overall_score": result.overall_score,
            "decision": result.decision,
            "confidence": result.confidence,
            "analysis_status": "completed",
        },
        "analysis_scores": {
            "market_score": result.market.market_score,
            "operational_score": result.operational.operational_score,
            "financial_score": result.financial.financial_score,
            "risk_score": result.risk.feasibility_risk_score,
            "overall_score": result.overall_score,
        },
        "market_analyses": {
            "demand_score": result.market.demand_component / 0.35 if result.market.demand_component else 0,
            "competition_score": None,
            "market_gap_score": None,
            "pricing_score": None,
            "opportunity_score": None,
            "market_score": result.market.market_score,
        },
        "operational_analyses": {
            "operational_score": result.operational.operational_score,
        },
        "financial_analyses": {
            "estimated_project_cost": None,
            "available_capital": None,
            "funding_gap": result.financial.funding_gap,
            "estimated_monthly_revenue": None,
            "estimated_monthly_expenses": None,
            "estimated_monthly_profit": result.financial.monthly_profit,
            "break_even_months": result.financial.estimated_break_even_months,
        },
        "analysis_risks": [
            {
                "risk_type": r.risk_type,
                "risk_score": r.risk_score,
                "severity": result.risk.severity,
                "description": r.description,
                "mitigation": r.mitigation,
            }
            for r in result.risk.risks
        ],
        "analysis_recommendations": [
            {
                "category": "Business Strategy",
                "priority": "High" if result.decision in ("Needs Modification", "Reconsider") else "Medium",
                "recommendation": r,
                "expected_impact": "Improves feasibility by addressing identified constraints.",
            }
            for r in result.recommendations
        ],
    }
