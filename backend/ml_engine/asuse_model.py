"""ASUSE 2023-24 outcome-model adapter for the UdyamSetu decision engine.

The trained ASUSE model uses establishment-level survey features.  UdyamSetu's
user context is a different schema, so this module is the explicit boundary
between the two.  It converts known user/profile information into ASUSE-shaped
features, allows exact ASUSE-coded overrides when available, and returns a
prediction that the decision engine can safely consume.

Important: ASUSE is a cross-sectional survey.  The prediction is an historical
association signal, not a guarantee of future business success.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import joblib
import numpy as np
import pandas as pd

from .profile_loader import BusinessProfile
from .recommendation_engine import UserBusinessContext

ASUSE_FEATURE_COLUMNS = [
    "sector", "district", "location", "major_nic_2dig", "major_nic_5dig",
    "ownership_type", "education_level", "technical_training", "num_eco_activities",
    "bank_account", "est_type", "years_of_operation", "months_operated",
    "daily_work_hours", "accounts_maintained", "used_computer", "used_internet",
    "registered", "manuf_services", "contract_manuf_service", "franchise",
    "total_workers", "fixed_assets_owned", "fixed_assets_hired", "net_additions_assets",
]

# Conservative defaults taken from the ASUSE training frame's modal codes.
# They are deliberately centralized and can be overridden through context.
DEFAULT_ASUSE_VALUES: Dict[str, Any] = {
    "sector": 1,
    "district": 1,
    "location": 2,
    "major_nic_2dig": 47,
    "major_nic_5dig": 14105,
    "ownership_type": 1,
    "education_level": 3.0,
    "technical_training": 2.0,
    "num_eco_activities": 1,
    "bank_account": 1,
    "est_type": 2,
    "years_of_operation": 1.0,
    "months_operated": 12.0,
    "daily_work_hours": 8.0,
    "accounts_maintained": 2,
    "used_computer": 2,
    "used_internet": 2,
    "registered": 2,
    "manuf_services": 2,
    "contract_manuf_service": 2.0,
    "franchise": 2,
    "total_workers": 1.0,
    "fixed_assets_owned": 0.0,
    "fixed_assets_hired": 0.0,
    "net_additions_assets": 0.0,
}

# NIC-2 approximations for the project's reference-profile categories. These
# are only used when an exact ASUSE NIC code is not supplied. The adapter keeps
# the mapping visible and reports that it was inferred.
NIC2_BY_CATEGORY = {
    "food processing": 10,
    "manufacturing": 31,
    "services": 95,
}
NIC2_BY_SUBCATEGORY = {
    "bakery": 10,
    "pickles": 10,
    "flour milling": 10,
    "spice processing": 10,
    "fruit processing": 10,
    "traditional snacks": 10,
    "millet processing": 10,
    "millet foods": 10,
    "personal care products": 20,
    "cosmetics": 20,
    "cleaning products": 20,
    "electronics": 26,
    "garments": 14,
    "footwear": 15,
    "furniture": 31,
    "wood products": 16,
    "metal products": 25,
    "personal care": 96,
    "electronics repair": 95,
    "digital services": 62,
}

# ASUSE covers non-agricultural unincorporated establishments. These profiles
# should not receive an ASUSE score unless the product has a defensible way to
# map them to a covered non-agricultural activity.
OUT_OF_ASUSE_SCOPE_CATEGORIES = {"agriculture allied"}


@dataclass(frozen=True)
class ASUSEPrediction:
    applicable: bool
    profitability_tier: Optional[str]
    probabilities: Dict[str, float]
    viability_score: Optional[float]
    model_version: str
    model_path: Optional[str]
    features: Dict[str, Any] = field(default_factory=dict)
    inferred_features: tuple[str, ...] = ()
    reason: str = ""

    @property
    def model_used(self) -> bool:
        return self.applicable and self.profitability_tier is not None


class ASUSEProfitabilityModel:
    """Load and apply the trainable ASUSE Random Forest pipeline."""

    def __init__(self, model_path: str | Path = "models/asuse_profitability.joblib"):
        self.model_path = str(model_path)
        self._model = None
        self.model_version = "asuse-profitability-unknown"

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    def load(self) -> "ASUSEProfitabilityModel":
        payload = joblib.load(self.model_path)
        # train_asuse_model currently saves the sklearn Pipeline directly.
        # Supporting a metadata wrapper makes future model versioning backwards
        # compatible without changing the runtime contract.
        if isinstance(payload, dict) and "model" in payload:
            self._model = payload["model"]
            self.model_version = str(payload.get("model_version", Path(self.model_path).stem))
        else:
            self._model = payload
            self.model_version = Path(self.model_path).stem
        return self

    def predict(
        self,
        context: UserBusinessContext,
        profile: BusinessProfile,
        generated=None,
    ) -> ASUSEPrediction:
        if not self.is_loaded:
            self.load()

        category = str(profile.category or "").strip().lower()
        if category in OUT_OF_ASUSE_SCOPE_CATEGORIES:
            return ASUSEPrediction(
                applicable=False,
                profitability_tier=None,
                probabilities={},
                viability_score=None,
                model_version=self.model_version,
                model_path=self.model_path,
                reason=("ASUSE is not applied to this profile because the reference "
                        "category is outside the survey's non-agricultural scope."),
            )

        features, inferred = build_asuse_features(context, profile, generated)
        frame = pd.DataFrame([features], columns=ASUSE_FEATURE_COLUMNS)
        prediction = self._model.predict(frame)[0]
        probabilities: Dict[str, float] = {}
        if hasattr(self._model, "predict_proba"):
            raw = self._model.predict_proba(frame)[0]
            classes = getattr(self._model, "classes_", None)
            if classes is None:
                # Pipeline delegates classes_ to the final estimator in sklearn.
                classes = getattr(getattr(self._model, "named_steps", {}).get("model"), "classes_", [])
            probabilities = {str(label): round(float(prob), 6) for label, prob in zip(classes, raw)}

        # Expected score using fixed ordinal anchors. This is a decision-support
        # score, not a probability and not a claim of expected monetary profit.
        anchors = {"low": 20.0, "medium": 60.0, "high": 90.0}
        viability = round(sum(probabilities.get(k, 0.0) * v for k, v in anchors.items()), 2)
        if not probabilities:
            viability = anchors.get(str(prediction), 50.0)

        return ASUSEPrediction(
            applicable=True,
            profitability_tier=str(prediction),
            probabilities=probabilities,
            viability_score=viability,
            model_version=self.model_version,
            model_path=self.model_path,
            features=features,
            inferred_features=tuple(inferred),
            reason="ASUSE historical profitability signal generated from ASUSE-compatible establishment features.",
        )


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or (isinstance(value, float) and np.isnan(value)):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _code(value: Any, default: Any) -> Any:
    if value in (None, ""):
        return default
    try:
        number = float(value)
        return int(number) if number.is_integer() else number
    except (TypeError, ValueError):
        return value


def _infer_nic2(profile: BusinessProfile) -> Optional[int]:
    sub = str(profile.subcategory or "").strip().lower()
    if sub in NIC2_BY_SUBCATEGORY:
        return NIC2_BY_SUBCATEGORY[sub]
    category = str(profile.category or "").strip().lower()
    return NIC2_BY_CATEGORY.get(category)


def build_asuse_features(
    context: UserBusinessContext,
    profile: BusinessProfile,
    generated=None,
) -> tuple[Dict[str, Any], list[str]]:
    """Convert UdyamSetu context/profile into the ASUSE model's input schema."""
    overrides = dict(getattr(context, "asuse_overrides", {}) or {})
    values = dict(DEFAULT_ASUSE_VALUES)
    inferred: list[str] = []

    # User-provided exact survey-coded values always win.
    for name, value in overrides.items():
        if name in values and value not in (None, ""):
            values[name] = value

    # Derive only features for which UdyamSetu has a defensible source.
    if "total_workers" not in overrides:
        planned_workers = getattr(context, "planned_workers", None)
        if planned_workers is not None:
            values["total_workers"] = max(0.0, _num(planned_workers, 1.0))
        else:
            inferred.append("total_workers")

    if "years_of_operation" not in overrides:
        business_age = getattr(context, "business_age_years", None)
        if business_age is not None:
            values["years_of_operation"] = max(0.0, _num(business_age, 1.0))
        else:
            inferred.append("years_of_operation")

    if "daily_work_hours" not in overrides:
        work_hours = getattr(context, "daily_work_hours", None)
        if work_hours is not None:
            values["daily_work_hours"] = max(0.0, _num(work_hours, 8.0))
        else:
            inferred.append("daily_work_hours")

    if "major_nic_2dig" not in overrides:
        nic2 = _infer_nic2(profile)
        if nic2 is not None:
            values["major_nic_2dig"] = nic2
            inferred.append("major_nic_2dig")
        else:
            inferred.append("major_nic_2dig")

    # A 5-digit NIC cannot be safely inferred from a natural-language profile
    # without a maintained official codebook. Keep the trained modal code unless
    # the application supplies the exact code.
    if "major_nic_5dig" not in overrides:
        inferred.append("major_nic_5dig")

    # Map broad UdyamSetu category to ASUSE's manufacturing/services indicator.
    if "manuf_services" not in overrides:
        category = str(profile.category or "").lower()
        if "manufactur" in category or "food processing" in category:
            values["manuf_services"] = 1
        elif "service" in category:
            values["manuf_services"] = 2
        inferred.append("manuf_services")

    # Financial asset values can be approximated from the reference project cost
    # only when no explicit ASUSE-style asset inputs exist. To avoid inventing a
    # strong signal, leave the survey defaults unless exact values are provided.
    for name in ("fixed_assets_owned", "fixed_assets_hired", "net_additions_assets"):
        if name not in overrides:
            inferred.append(name)

    # Normalize numeric values expected by the trained pipeline.
    for name in [
        "years_of_operation", "months_operated", "daily_work_hours", "num_eco_activities",
        "total_workers", "fixed_assets_owned", "fixed_assets_hired", "net_additions_assets",
    ]:
        values[name] = _num(values[name], DEFAULT_ASUSE_VALUES[name])

    return {name: values[name] for name in ASUSE_FEATURE_COLUMNS}, inferred
