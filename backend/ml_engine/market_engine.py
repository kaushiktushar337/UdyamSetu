from dataclasses import dataclass
from typing import List


@dataclass
class MarketInput:
    demand_score: float
    competition_score: float
    opportunity_score: float
    pricing_score: float


@dataclass
class MarketResult:
    demand_component: float
    competition_component: float
    opportunity_component: float
    pricing_component: float
    market_score: float
    rating: str
    recommendations: List[str]


DEFAULT_MARKET_WEIGHTS = {
    "demand": 0.35,
    "competition": 0.25,
    "opportunity": 0.25,
    "pricing": 0.15,
}


def clamp(value: float) -> float:
    return max(0.0, min(100.0, float(value)))


def calculate_market_feasibility(
    data: MarketInput,
    weights: dict | None = None
) -> MarketResult:
    weights = weights or DEFAULT_MARKET_WEIGHTS

    demand = clamp(data.demand_score)
    competition = clamp(data.competition_score)
    opportunity = clamp(data.opportunity_score)
    pricing = clamp(data.pricing_score)

    # Higher competition reduces market attractiveness.
    effective_competition = 100.0 - competition

    demand_component = demand * weights["demand"]
    competition_component = effective_competition * weights["competition"]
    opportunity_component = opportunity * weights["opportunity"]
    pricing_component = pricing * weights["pricing"]

    market_score = round(
        demand_component
        + competition_component
        + opportunity_component
        + pricing_component,
        2,
    )

    if market_score >= 80:
        rating = "Strong"
    elif market_score >= 65:
        rating = "Good"
    elif market_score >= 45:
        rating = "Moderate"
    else:
        rating = "Weak"

    recommendations = []

    if demand < 40:
        recommendations.append(
            "Local demand appears weak. Validate customer demand before investing heavily."
        )
    elif demand >= 70:
        recommendations.append(
            "Demand appears strong under the current market assumptions."
        )
    else:
        recommendations.append(
            "Demand is moderate. Start with a controlled scale and validate customer response."
        )

    if competition >= 75:
        recommendations.append(
            "Competition is high. Differentiation through price, service, quality, or location will be important."
        )
    elif competition >= 45:
        recommendations.append(
            "Competition is moderate. Study competitors before finalizing positioning."
        )
    else:
        recommendations.append(
            "Competition appears relatively low, which may provide an entry opportunity."
        )

    if opportunity < 40:
        recommendations.append(
            "The identified market opportunity is limited. Consider modifying the business model or target segment."
        )
    elif opportunity >= 70:
        recommendations.append(
            "The market opportunity score is promising under the current assumptions."
        )

    if pricing < 40:
        recommendations.append(
            "Pricing potential is weak. Review margins and willingness to pay before proceeding."
        )
    elif pricing >= 70:
        recommendations.append(
            "Pricing potential is favorable under the current assumptions."
        )

    return MarketResult(
        demand_component=round(demand_component, 2),
        competition_component=round(competition_component, 2),
        opportunity_component=round(opportunity_component, 2),
        pricing_component=round(pricing_component, 2),
        market_score=market_score,
        rating=rating,
        recommendations=recommendations,
    )
