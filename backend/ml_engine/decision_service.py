"""High-level service for the complete ML recommendation and decision workflow."""
from __future__ import annotations
from typing import Any, Dict, List, Optional

from .profile_loader import BusinessProfileLoader
from .location_metrics_loader import LocationMetricsLoader
from .recommendation_engine import UserBusinessContext
from .recommendation_pipeline import BusinessRecommendationPipeline
from .database_mapper import map_analysis_result
from .analysis_repository import AnalysisRepository
from .confidence import estimate_confidence


class UdyamSetuDecisionService:
    def __init__(self, pipeline: BusinessRecommendationPipeline, repository: AnalysisRepository | None = None):
        self.pipeline = pipeline
        self.repository = repository

    @classmethod
    def from_database(cls, database_url: str | None = None, calibrator=None) -> "UdyamSetuDecisionService":
        profiles = BusinessProfileLoader(database_url).load_profiles()
        location_loader = LocationMetricsLoader(database_url)
        pipeline = BusinessRecommendationPipeline(
            profiles=profiles,
            calibrator=calibrator,
            location_loader=location_loader,
        )
        return cls(pipeline, AnalysisRepository(database_url))

    def recommend(self, context: UserBusinessContext, top_k: int = 5) -> List[Dict[str, Any]]:
        results = self.pipeline.recommend(context, top_k=top_k)
        for item in results:
            item["confidence"] = estimate_confidence(
                item["match"].profile,
                item["generated_inputs"],
                item.get("calibration"),
            )
        return results

    def persist_result(
        self,
        item: Dict[str, Any],
        *,
        user_id: str,
        business_id: str,
        location_id: str,
    ) -> str:
        """Persist a selected recommendation.

        business_id intentionally refers to the EXISTING application business table,
        exactly as required by business_analyses. It is not replaced with profile_id.
        """
        if self.repository is None:
            raise RuntimeError("No AnalysisRepository is configured")
        payload = map_analysis_result(
            item["analysis"],
            item["analysis_input"],
            confidence=item.get("confidence"),
            engine_version=self.engine_version(item),
        )
        return self.repository.save_analysis(
            user_id=user_id,
            business_id=business_id,
            location_id=location_id,
            payload=payload,
        )

    @staticmethod
    def engine_version(item: Dict[str, Any]) -> str:
        calibration = item.get("calibration")
        if calibration is not None and calibration.model_used:
            return f"decision-engine-v1+{calibration.model_version}"
        return "decision-engine-v1"
