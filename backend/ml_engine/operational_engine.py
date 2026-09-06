from dataclasses import dataclass
from typing import List

@dataclass
class OperationalInput:
    resource_score: float
    infrastructure_score: float
    supply_chain_score: float
    logistics_score: float

@dataclass
class OperationalResult:
    operational_score: float
    rating: str
    recommendations: List[str]

DEFAULT_OPERATIONAL_WEIGHTS = {
    "resources": 0.30,
    "infrastructure": 0.25,
    "supply_chain": 0.25,
    "logistics": 0.20,
}

def _clamp(v):
    return max(0.0, min(100.0, float(v)))

def calculate_operational_feasibility(data: OperationalInput, weights=None):
    weights = weights or DEFAULT_OPERATIONAL_WEIGHTS
    score = (
        _clamp(data.resource_score) * weights["resources"] +
        _clamp(data.infrastructure_score) * weights["infrastructure"] +
        _clamp(data.supply_chain_score) * weights["supply_chain"] +
        _clamp(data.logistics_score) * weights["logistics"]
    )
    score = round(score, 2)

    rating = "Strong" if score >= 80 else "Good" if score >= 65 else "Moderate" if score >= 45 else "Weak"

    recs = []
    if data.resource_score < 50:
        recs.append("Improve access to the people, skills, equipment, or raw resources required for operations.")
    if data.infrastructure_score < 50:
        recs.append("Review infrastructure requirements before starting at full scale.")
    if data.supply_chain_score < 50:
        recs.append("Strengthen supplier availability and identify backup suppliers.")
    if data.logistics_score < 50:
        recs.append("Improve transport, delivery, or distribution arrangements.")
    if not recs:
        recs.append("Operational readiness is satisfactory under the current assumptions.")

    return OperationalResult(score, rating, recs)
