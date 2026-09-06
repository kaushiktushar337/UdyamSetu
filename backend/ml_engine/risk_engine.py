from dataclasses import dataclass
from typing import List

@dataclass
class RiskItem:
    risk_type: str
    risk_score: float
    description: str
    mitigation: str

@dataclass
class RiskInput:
    capital_coverage_ratio: float
    competition_score: float
    operational_score: float
    business_risks: List[RiskItem]

@dataclass
class RiskResult:
    overall_risk_score: float
    feasibility_risk_score: float
    severity: str
    risks: List[RiskItem]

def _clamp(v):
    return max(0.0, min(100.0, float(v)))

def calculate_risk(data: RiskInput):
    # Higher values represent more risk.
    capital_risk = _clamp((1 - min(max(data.capital_coverage_ratio, 0), 1)) * 100)
    competition_risk = _clamp(data.competition_score)
    operational_risk = _clamp(100 - data.operational_score)

    explicit = [_clamp(r.risk_score) for r in data.business_risks]
    explicit_risk = sum(explicit) / len(explicit) if explicit else 0

    overall = round(
        capital_risk * 0.30 +
        competition_risk * 0.20 +
        operational_risk * 0.25 +
        explicit_risk * 0.25, 2
    )

    feasibility_risk_score = round(100 - overall, 2)
    severity = "High" if overall >= 70 else "Medium" if overall >= 40 else "Low"

    generated = []
    if capital_risk >= 50:
        generated.append(RiskItem("Financial", capital_risk,
            "Available funding may be insufficient for the estimated project cost.",
            "Reduce initial scale, phase the investment, or arrange appropriate funding."))
    if competition_risk >= 70:
        generated.append(RiskItem("Competition", competition_risk,
            "The market appears highly competitive.",
            "Differentiate through pricing, service, quality, niche targeting, or location."))
    if operational_risk >= 50:
        generated.append(RiskItem("Operational", operational_risk,
            "Operational readiness is currently weak.",
            "Resolve key resource, infrastructure, supply-chain, or logistics gaps before scaling."))

    return RiskResult(overall, feasibility_risk_score, severity, generated + data.business_risks)
