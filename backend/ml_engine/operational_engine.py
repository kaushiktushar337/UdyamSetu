from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class OperationalInput:
    resource_score: float
    infrastructure_score: float
    supply_chain_score: float
    logistics_score: float

@dataclass
class OperationalGuidance:
    """Structured operational guidance for starting a business."""
    infrastructure_needed: List[str]
    staffing_requirements: Dict[str, int]
    typical_timeline_to_breakeven: str
    key_challenges: List[str]
    prerequisites: List[str]

@dataclass
class OperationalResult:
    operational_score: float
    rating: str
    recommendations: List[str]
    guidance: Optional[OperationalGuidance] = None

DEFAULT_OPERATIONAL_WEIGHTS = {
    "resources": 0.30,
    "infrastructure": 0.25,
    "supply_chain": 0.25,
    "logistics": 0.20,
}

def _clamp(v):
    return max(0.0, min(100.0, float(v)))

def calculate_operational_feasibility(data: OperationalInput, weights=None, profile=None, context=None):
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
    challenges = []
    prerequisites = []
    infrastructure_needed = []
    staffing = {"unskilled": 0, "skilled": 0, "total": 0}

    if data.resource_score < 50:
        recs.append("Improve access to the people, skills, equipment, or raw resources required for operations.")
        challenges.append("Resource availability may limit initial operations")
    if data.infrastructure_score < 50:
        recs.append("Review infrastructure requirements before starting at full scale.")
        challenges.append("Infrastructure setup needed before launch")
        infrastructure_needed.extend(["Basic workspace", "Power connection", "Water supply"])
    if data.supply_chain_score < 50:
        recs.append("Strengthen supplier availability and identify backup suppliers.")
        challenges.append("Supplier network needs development")
    if data.logistics_score < 50:
        recs.append("Improve transport, delivery, or distribution arrangements.")
        challenges.append("Distribution channel setup required")
    if not recs:
        recs.append("Operational readiness is satisfactory under the current assumptions.")
        challenges.append("Minor operational challenges possible")

    # Generate typical staffing based on score
    if score >= 65:
        staffing = {"unskilled": 1, "skilled": 1, "total": 2}
    elif score >= 45:
        staffing = {"unskilled": 2, "skilled": 1, "total": 3}
    else:
        staffing = {"unskilled": 2, "skilled": 2, "total": 4}

    # Estimate timeline to breakeven based on score
    if score >= 80:
        timeline = "3-4 months"
    elif score >= 65:
        timeline = "4-6 months"
    elif score >= 45:
        timeline = "6-9 months"
    else:
        timeline = "9-12 months or longer"

    # Add prerequisites based on challenges
    if challenges:
        prerequisites = [
            "Prepare business registration documents",
            "Open business bank account",
            "Obtain necessary licenses/permits",
            "Set up accounting system"
        ]

    # Generate guidance
    guidance = OperationalGuidance(
        infrastructure_needed=infrastructure_needed if infrastructure_needed else ["Basic setup available"],
        staffing_requirements=staffing,
        typical_timeline_to_breakeven=timeline,
        key_challenges=challenges if challenges else ["Market acceptance"],
        prerequisites=prerequisites if prerequisites else ["Standard business setup"]
    )

    return OperationalResult(score, rating, recs, guidance=guidance)
