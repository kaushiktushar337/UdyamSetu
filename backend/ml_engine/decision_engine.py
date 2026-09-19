from dataclasses import dataclass
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
    asuse_prediction: Optional[object] = None
    explanation: dict = None


# The explainable engine remains the majority of the final score.
# ASUSE contributes a bounded historical profitability signal and ISES
# contributes a bounded local business-environment signal. Neither replaces
# the financial/market/operational/risk analysis.
DEFAULT_FINAL_WEIGHTS = {
    "financial": 0.23,
    "market": 0.23,
    "operational": 0.15,
    "risk": 0.14,
    "asuse": 0.15,
    "ises": 0.10,
}


def _ises_score(ises_context):
    if not ises_context:
        return None
    value = ises_context.get("environment_score")
    try:
        return max(0.0, min(100.0, float(value))) if value is not None else None
    except (TypeError, ValueError):
        return None


def _extract_market_context(ises_context, location_metrics=None):
    """Extract structured market context from ISES and location metrics."""
    context = {
        "data_sources": [],
        "data_quality": "limited",
        "category_stats": {},
        "available_indicators": []
    }

    # Check ISES data
    if ises_context and isinstance(ises_context, dict):
        context["data_sources"].append("ISES 2022")

        # Extract key metrics
        metrics = [
            ("ises_profit_business_pct", "profit_business_pct"),
            ("ises_avg_monthly_sales", "avg_monthly_sales"),
            ("ises_avg_workers", "avg_workers"),
            ("ises_bank_account_pct", "bank_account_pct"),
            ("ises_business_loan_pct", "business_loan_pct"),
            ("ises_competitor_monitoring_pct", "competitor_monitoring_pct"),
        ]

        for metric_key, display_key in metrics:
            if metric_key in ises_context:
                context["category_stats"][display_key] = ises_context[metric_key]
                context["available_indicators"].append(display_key)

        if context["available_indicators"]:
            context["data_quality"] = "good"

    # Add location metrics if available
    if location_metrics and isinstance(location_metrics, dict):
        context["data_sources"].append("Local Market Metrics")

        location_stats = {
            "demand_score": location_metrics.get("demand_score"),
            "competition_score": location_metrics.get("competition_score"),
            "opportunity_score": location_metrics.get("opportunity_score"),
            "competition_count": location_metrics.get("competition_count"),
        }

        for key, value in location_stats.items():
            if value is not None:
                context["category_stats"][key] = value
                context["available_indicators"].append(key)

    # Clean up
    if not context["data_sources"]:
        context["data_sources"] = ["No local data available"]
        context["data_quality"] = "extrapolated"

    return context


def _build_explanation(financial, market, operational, risk, asuse_prediction, ises_context, weights, overall, decision, location_metrics=None):
    """Build a frontend-ready, human-readable explanation of the decision.

    The explanation describes score contributions and notable strengths/concerns.
    It does not claim causality or guaranteed business success.
    """
    components = {
        "financial": round(float(financial.financial_score), 2),
        "market": round(float(market.market_score), 2),
        "operational": round(float(operational.operational_score), 2),
        "risk": round(float(risk.feasibility_risk_score), 2),
    }
    contributions = {name: round(score * float(weights.get(name, 0.0)), 2) for name, score in components.items()}
    asuse_info = None
    if asuse_prediction is not None:
        applicable = bool(getattr(asuse_prediction, "applicable", False))
        asuse_score = getattr(asuse_prediction, "viability_score", None)
        asuse_info = {
            "applicable": applicable,
            "tier": getattr(asuse_prediction, "profitability_tier", None),
            "viability_score": round(float(asuse_score), 2) if asuse_score is not None else None,
            "probabilities": dict(getattr(asuse_prediction, "probabilities", {}) or {}),
            "model_version": getattr(asuse_prediction, "model_version", None),
            "inferred_features": list(getattr(asuse_prediction, "inferred_features", ()) or ()),
            "reason": getattr(asuse_prediction, "reason", ""),
        }
        if applicable and asuse_score is not None:
            contributions["asuse"] = round(float(asuse_score) * float(weights.get("asuse", 0.0)), 2)
            components["asuse"] = round(float(asuse_score), 2)

    ises_score = _ises_score(ises_context)
    if ises_score is not None:
        components["ises"] = round(ises_score, 2)
        contributions["ises"] = round(ises_score * float(weights.get("ises", 0.0)), 2)

    strengths = []
    concerns = []
    labels = {
        "financial": "financial feasibility",
        "market": "market conditions",
        "operational": "operational readiness",
        "risk": "risk-adjusted feasibility",
        "asuse": "historical profitability signal",
        "ises": "local business environment",
    }
    for name, score in sorted(components.items(), key=lambda x: x[1], reverse=True):
        if score >= 75:
            strengths.append(f"Strong {labels[name]} ({score:.1f}/100).")
        elif score < 50:
            concerns.append(f"{labels[name].capitalize()} is a constraint ({score:.1f}/100).")

    if risk.severity == "High":
        concerns.append("High-severity business risks should be addressed before full-scale investment.")
    elif risk.severity == "Medium":
        concerns.append("Some business risks should be mitigated before scaling.")

    if asuse_info and asuse_info["applicable"] and asuse_info["inferred_features"]:
        concerns.append("The historical profitability signal uses inferred/default values for some features; exact user inputs can improve it.")
    if asuse_info and not asuse_info["applicable"]:
        concerns.append("The historical profitability model was not applied because this business is outside its supported scope.")

    # Extract market context from ISES and location metrics
    market_context = _extract_market_context(ises_context, location_metrics)

    return {
        "decision": decision,
        "overall_score": round(float(overall), 2),
        "score_components": components,
        "score_contributions": contributions,
        "weights": {k: float(v) for k, v in weights.items()},
        "strengths": strengths[:4],
        "concerns": concerns[:5],
        "asuse": asuse_info,
        "ises": {
            "available": ises_score is not None,
            "environment_score": ises_score,
        },
        "market_context": market_context,
        "summary": f"Final score {overall:.1f}/100: {decision}.",
    }


def calculate_business_analysis(data: BusinessAnalysisInput, weights=None, asuse_prediction=None, ises_context=None, location_metrics=None):
    weights = dict(DEFAULT_FINAL_WEIGHTS if weights is None else weights)

    asuse_score_available = (
        asuse_prediction is not None
        and getattr(asuse_prediction, "applicable", False)
        and getattr(asuse_prediction, "viability_score", None) is not None
    )
    ises_score_available = _ises_score(ises_context) is not None

    if asuse_score_available and ises_score_available:
        weights = dict(DEFAULT_FINAL_WEIGHTS)
    elif asuse_score_available:
        weights = {
            "financial": 0.255,
            "market": 0.255,
            "operational": 0.170,
            "risk": 0.170,
            "asuse": 0.150,
        }
    elif ises_score_available:
        weights = {
            "financial": 0.270,
            "market": 0.270,
            "operational": 0.180,
            "risk": 0.180,
            "ises": 0.100,
        }
    else:
        weights = {
            "financial": 0.30,
            "market": 0.30,
            "operational": 0.20,
            "risk": 0.20,
        }

    # Normalize custom weights too, so the final score is always a true
    # 0-100 weighted composite.
    total = sum(weights.values()) or 1.0
    weights = {key: value / total for key, value in weights.items()}

    financial = calculate_financial_feasibility(data.financial)
    market = calculate_market_feasibility(data.market)
    operational = calculate_operational_feasibility(data.operational)

    risk = calculate_risk(RiskInput(
        capital_coverage_ratio=financial.capital_coverage_ratio,
        competition_score=data.market.competition_score,
        operational_score=operational.operational_score,
        business_risks=data.business_risks,
    ))

    base_score = (
        financial.financial_score * weights["financial"] +
        market.market_score * weights["market"] +
        operational.operational_score * weights["operational"] +
        risk.feasibility_risk_score * weights["risk"]
    )
    asuse_score = None
    if asuse_prediction is not None and getattr(asuse_prediction, "applicable", False):
        asuse_score = getattr(asuse_prediction, "viability_score", None)
    ises_score = _ises_score(ises_context)
    if asuse_score is not None and "asuse" in weights:
        base_score += float(asuse_score) * weights["asuse"]
    if ises_score is not None and "ises" in weights:
        base_score += float(ises_score) * weights["ises"]
    overall = round(base_score, 2)

    if overall >= 80:
        decision = "Highly Viable"
    elif overall >= 65:
        decision = "Viable"
    elif overall >= 45:
        decision = "Needs Modification"
    else:
        decision = "Reconsider"

    confidence = "Combined historical + local signals" if (asuse_score is not None or ises_score is not None) else "Prototype / rule-based"

    recommendations = []
    recommendations.extend(financial.recommendations)
    recommendations.extend(market.recommendations)
    recommendations.extend(operational.recommendations)

    if risk.severity == "High":
        recommendations.append("Address high-severity risks before committing to full-scale investment.")

    if asuse_prediction is not None and getattr(asuse_prediction, "applicable", False):
        tier = getattr(asuse_prediction, "profitability_tier", None)
        if tier == "high":
            recommendations.append("Historical profitability signal is favorable; validate local demand and costs before investment.")
        elif tier == "medium":
            recommendations.append("Historical profitability signal is moderate; validate pricing, costs, and operating assumptions before scaling.")
        elif tier == "low":
            recommendations.append("Historical profitability signal is weaker; consider reducing scale and strengthening the business model before investment.")

    if ises_score is not None:
        if ises_score >= 75:
            recommendations.append("Local business conditions are supportive; validate your own costs and capacity before scaling.")
        elif ises_score < 45:
            recommendations.append("Local business conditions show constraints; test the model at smaller scale and address operational gaps first.")

    recommendations = list(dict.fromkeys(recommendations))
    explanation = _build_explanation(
        financial, market, operational, risk, asuse_prediction, ises_context, weights, overall, decision, location_metrics
    )

    return BusinessAnalysisResult(
        overall_score=overall,
        decision=decision,
        confidence=confidence,
        financial=financial,
        market=market,
        operational=operational,
        risk=risk,
        recommendations=recommendations,
        asuse_prediction=asuse_prediction,
        explanation=explanation,
    )


def result_for_database(result, analysis_input=None):
    """Map engine output to the agreed PostgreSQL write-table contract.

    The current database schema has no dedicated ASUSE prediction table, so the
    prediction is not silently written into an unrelated column. It is retained
    on the in-memory result/API response; persistence continues to use only the
    agreed tables.
    """
    financial_input = analysis_input.financial if analysis_input else None
    market_input = analysis_input.market if analysis_input else None
    operational_input = analysis_input.operational if analysis_input else None

    payload = {
        "business_analyses": {
            "overall_score": result.overall_score,
            "decision": result.decision,
            "confidence": 0.65,
            "analysis_status": "completed",
            "engine_version": "decision-engine-v3-combined" if (
                result.asuse_prediction is not None
                or result.explanation.get("ises", {}).get("available")
            ) else "decision-engine-v1",
        },
        "analysis_scores": {
            "market_score": result.market.market_score,
            "operational_score": result.operational.operational_score,
            "financial_score": result.financial.financial_score,
            "risk_score": result.risk.feasibility_risk_score,
            "overall_score": result.overall_score,
        },
        "market_analyses": {
            "demand_score": market_input.demand_score if market_input else result.market.demand_component / 0.35,
            "competition_score": market_input.competition_score if market_input else None,
            "market_gap_score": None,
            "pricing_score": market_input.pricing_score if market_input else None,
            "opportunity_score": market_input.opportunity_score if market_input else None,
        },
        "operational_analyses": {
            "resource_score": operational_input.resource_score if operational_input else None,
            "infrastructure_score": operational_input.infrastructure_score if operational_input else None,
            "supply_chain_score": operational_input.supply_chain_score if operational_input else None,
            "logistics_score": operational_input.logistics_score if operational_input else None,
            "operational_score": result.operational.operational_score,
        },
        "financial_analyses": {
            "estimated_project_cost": financial_input.estimated_project_cost if financial_input else None,
            "available_capital": (financial_input.available_capital + financial_input.funding_available) if financial_input else None,
            "funding_gap": result.financial.funding_gap,
            "estimated_monthly_revenue": financial_input.estimated_monthly_revenue if financial_input else None,
            "estimated_monthly_expenses": financial_input.estimated_monthly_expenses if financial_input else None,
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
    return payload
