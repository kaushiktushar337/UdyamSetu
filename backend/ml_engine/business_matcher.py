"""
Lightweight semantic business matcher for UdyamSetu.

Uses paraphrase-multilingual-MiniLM-L12-v2 (384 dimensions), the same
small multilingual embedding model already used by the knowledge-search layer.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable, List, Optional

import numpy as np

from .profile_loader import BusinessProfile


@dataclass
class BusinessMatch:
    profile: BusinessProfile
    semantic_score: float
    capital_score: float
    final_score: float
    reasons: List[str]


class BusinessMatcher:
    def __init__(
        self,
        model_name: Optional[str] = None,
        semantic_weight: float = 0.75,
        capital_weight: float = 0.25,
    ):
        self.model_name = model_name or os.getenv(
            "MODEL_NAME", "paraphrase-multilingual-MiniLM-L12-v2"
        )
        self.semantic_weight = semantic_weight
        self.capital_weight = capital_weight
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError("sentence-transformers is required for semantic matching. Install requirements.txt before running the full pipeline.") from exc
        self.model = SentenceTransformer(self.model_name)

        self._profiles: List[BusinessProfile] = []
        self._profile_embeddings: Optional[np.ndarray] = None

    def fit(self, profiles: Iterable[BusinessProfile]) -> "BusinessMatcher":
        self._profiles = list(profiles)
        if not self._profiles:
            raise ValueError("At least one business profile is required")

        texts = [profile.searchable_text() for profile in self._profiles]
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
        ).astype(np.float32)

        if embeddings.shape[1] != 384:
            raise ValueError(
                f"Expected 384-dimensional embeddings, got {embeddings.shape[1]}"
            )

        self._profile_embeddings = embeddings
        return self

    @staticmethod
    def _capital_score(available_capital: Optional[float], profile: BusinessProfile) -> float:
        """
        Returns a feasibility score from 0-100.

        Missing capital/project-cost data does not mean failure; it receives a
        neutral score so semantic matching can still surface the profile.
        """
        if available_capital is None:
            return 50.0

        required = profile.minimum_capital or profile.typical_project_cost
        if required is None or float(required) <= 0:
            return 50.0

        ratio = max(0.0, float(available_capital)) / float(required)

        if ratio >= 1.0:
            return 100.0
        return round(max(0.0, ratio * 100.0), 2)

    def match(
        self,
        user_text: str,
        available_capital: Optional[float] = None,
        top_k: int = 5,
    ) -> List[BusinessMatch]:
        if self._profile_embeddings is None:
            raise RuntimeError("Call fit(profiles) before match()")

        query = self.model.encode(
            user_text,
            normalize_embeddings=True,
            convert_to_numpy=True,
        ).astype(np.float32)

        if len(query) != 384:
            raise ValueError(f"Expected 384-dimensional query embedding, got {len(query)}")

        similarities = np.dot(self._profile_embeddings, query)

        matches: List[BusinessMatch] = []
        for profile, similarity in zip(self._profiles, similarities):
            semantic_score = round(float((similarity + 1.0) / 2.0 * 100.0), 2)
            capital_score = self._capital_score(available_capital, profile)

            final_score = round(
                semantic_score * self.semantic_weight
                + capital_score * self.capital_weight,
                2,
            )

            reasons = []
            if semantic_score >= 75:
                reasons.append("Strong semantic match with the user's business interests.")
            elif semantic_score >= 60:
                reasons.append("Relevant semantic match with the user's requirements.")

            if available_capital is not None:
                required = profile.minimum_capital or profile.typical_project_cost
                if required:
                    if available_capital >= required:
                        reasons.append("Available capital can cover the reference project cost.")
                    else:
                        gap = float(required) - float(available_capital)
                        reasons.append(f"Reference project cost exceeds available capital by approximately ₹{gap:,.0f}.")
                else:
                    reasons.append("No verified reference project cost is available for capital comparison.")

            matches.append(
                BusinessMatch(
                    profile=profile,
                    semantic_score=semantic_score,
                    capital_score=capital_score,
                    final_score=final_score,
                    reasons=reasons,
                )
            )

        matches.sort(key=lambda item: item.final_score, reverse=True)
        return matches[:max(1, top_k)]


def build_user_business_query(
    interests: Optional[str] = None,
    skills: Optional[str] = None,
    preferences: Optional[str] = None,
    location_context: Optional[str] = None,
) -> str:
    """Builds a clean semantic query without forcing users into rigid categories."""
    parts = []
    if interests:
        parts.append(f"Business interests: {interests}")
    if skills:
        parts.append(f"Skills and experience: {skills}")
    if preferences:
        parts.append(f"Preferences: {preferences}")
    if location_context:
        parts.append(f"Location context: {location_context}")

    text = "\n".join(parts).strip()
    if not text:
        raise ValueError("At least one business interest, skill, preference, or location context is required")
    return text
