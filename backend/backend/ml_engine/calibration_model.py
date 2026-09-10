"""Small optional calibration model for UdyamSetu.

The production baseline remains the explainable Decision Engine. This model is
only applied after it has been trained on real labelled outcomes. Ridge
regression is intentionally small, fast and easy to version/replace later.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import joblib
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from .feature_extractor import FEATURE_NAMES, FEATURE_SCHEMA_VERSION, FeatureVector


@dataclass
class CalibrationPrediction:
    score: float
    model_used: bool
    model_version: str
    reason: str


class ScoreCalibrator:
    def __init__(self, model_version: str = "calibration-ridge-v1"):
        self.model_version = model_version
        self._model: Pipeline | None = None

    @property
    def is_trained(self) -> bool:
        return self._model is not None

    def fit(self, features: Iterable[FeatureVector], targets: Sequence[float]) -> "ScoreCalibrator":
        rows = list(features)
        if len(rows) < 20:
            raise ValueError("At least 20 labelled real outcomes are required before calibration training.")
        if len(rows) != len(targets):
            raise ValueError("Feature and target counts must match.")
        if any(row.schema_version != FEATURE_SCHEMA_VERSION for row in rows):
            raise ValueError("Feature schema version mismatch.")

        X = np.array([row.ordered() for row in rows], dtype=float)
        y = np.clip(np.asarray(targets, dtype=float), 0.0, 100.0)
        self._model = Pipeline([
            ("scaler", StandardScaler()),
            ("ridge", Ridge(alpha=2.0)),
        ])
        self._model.fit(X, y)
        return self

    def predict(self, features: FeatureVector, fallback_score: float) -> CalibrationPrediction:
        fallback = float(max(0.0, min(100.0, fallback_score)))
        if not self.is_trained:
            return CalibrationPrediction(
                score=fallback,
                model_used=False,
                model_version=self.model_version,
                reason="No trained calibration model is available; the explainable decision-engine score was retained.",
            )
        if features.schema_version != FEATURE_SCHEMA_VERSION:
            return CalibrationPrediction(
                score=fallback,
                model_used=False,
                model_version=self.model_version,
                reason="Feature schema version mismatch; the explainable decision-engine score was retained.",
            )
        prediction = float(self._model.predict(np.array([features.ordered()], dtype=float))[0])
        return CalibrationPrediction(
            score=round(max(0.0, min(100.0, prediction)), 2),
            model_used=True,
            model_version=self.model_version,
            reason="Score adjusted by the trained calibration model.",
        )

    def save(self, path: str | Path) -> None:
        if not self.is_trained:
            raise RuntimeError("Cannot save an untrained calibration model.")
        joblib.dump({
            "model": self._model,
            "model_version": self.model_version,
            "feature_schema_version": FEATURE_SCHEMA_VERSION,
            "feature_names": FEATURE_NAMES,
        }, path)

    @classmethod
    def load(cls, path: str | Path) -> "ScoreCalibrator":
        payload = joblib.load(path)
        if payload.get("feature_schema_version") != FEATURE_SCHEMA_VERSION:
            raise ValueError("Saved model uses an incompatible feature schema.")
        if tuple(payload.get("feature_names", ())) != FEATURE_NAMES:
            raise ValueError("Saved model feature order does not match the current feature schema.")
        instance = cls(payload.get("model_version", "calibration-ridge-v1"))
        instance._model = payload["model"]
        return instance
