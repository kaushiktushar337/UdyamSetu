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
from .asuse_model import ASUSEProfitabilityModel
from .funding_service import FundingService
from pathlib import Path


class UdyamSetuDecisionService:
    def __init__(self, pipeline: BusinessRecommendationPipeline, repository: AnalysisRepository | None = None, funding_service: FundingService | None = None):
        self.pipeline = pipeline
        self.repository = repository
        self.funding_service = funding_service

    @classmethod
    def from_database(cls, database_url: str | None = None, calibrator=None, asuse_model_path: str | None = "models/asuse_profitability.json") -> "UdyamSetuDecisionService":
        profiles = BusinessProfileLoader(database_url).load_profiles()
        location_loader = LocationMetricsLoader(database_url)
        asuse_model = None
        if asuse_model_path and Path(asuse_model_path).exists():
            asuse_model = ASUSEProfitabilityModel(asuse_model_path).load()
        pipeline = BusinessRecommendationPipeline(
            profiles=profiles,
            calibrator=calibrator,
            location_loader=location_loader,
            asuse_model=asuse_model,
        )
        return cls(pipeline, AnalysisRepository(database_url), FundingService(database_url))

    def recommend(self, context: UserBusinessContext, top_k: int = 5) -> List[Dict[str, Any]]:
        results = self.pipeline.recommend(context, top_k=top_k)
        for item in results:
            item["confidence"] = estimate_confidence(
                item["match"].profile,
                item["generated_inputs"],
                item.get("calibration"),
                item.get("asuse_prediction"),
            )

        # Generate alternatives (rank 2-4) with reasoning
        alternatives = []
        if len(results) > 1:
            top_score = results[0].get("analysis", {}).get("overall_score", 0)
            for i, alt in enumerate(results[1:min(4, len(results))], start=2):
                alt_analysis = alt.get("analysis", {})
                alt_score = alt_analysis.get("overall_score", 0)

                # Build reasons why not selected
                reasons = []
                if alt_score < top_score - 10:
                    reasons.append(f"Lower overall feasibility score ({alt_score:.0f} vs {top_score:.0f})")

                # Check market score difference
                top_market = results[0].get("analysis", {}).get("market", {})
                alt_market = alt_analysis.get("market", {})
                if top_market and alt_market:
                    if top_market.get("market_score", 0) > alt_market.get("market_score", 0) + 10:
                        reasons.append("Weaker market conditions in this location")

                # Check capital requirements
                top_fin = results[0].get("generated_inputs", {}).get("financial", {})
                alt_fin = alt.get("generated_inputs", {}).get("financial", {})
                if top_fin and alt_fin:
                    if alt_fin.estimated_project_cost > top_fin.estimated_project_cost * 1.2:
                        reasons.append("Higher capital requirement than recommended option")

                # Check ASUSE profitability signal
                top_asuse = results[0].get("asuse_prediction")
                alt_asuse = alt.get("asuse_prediction")
                if top_asuse and not alt_asuse:
                    reasons.append("Historical profitability signal not available for this category")
                elif top_asuse and alt_asuse:
                    top_tier = getattr(top_asuse, 'profitability_tier', None)
                    alt_tier = getattr(alt_asuse, 'profitability_tier', None)
                    if top_tier and alt_tier and top_tier != alt_tier:
                        reasons.append(f"Historical profitability is {alt_tier} tier vs {top_tier}")

                if not reasons:
                    reasons.append(f"Alternative option with score {alt_score:.0f}/100")

                alternatives.append({
                    "rank": i,
                    "business_name": alt.get("business_name", ""),
                    "category": alt.get("match", {}).get("profile", {}).get("category", ""),
                    "score": round(alt_score, 2),
                    "decision": alt_analysis.get("decision", ""),
                    "why_not_selected": reasons[:3],
                    "profile_id": alt.get("profile_id", "")
                })

        # Add alternatives to top result
        if results:
            results[0]["alternatives"] = alternatives

            # Add funding and next steps to top result
            if self.funding_service is not None:
                try:
                    top = results[0]
                    financial = top["generated_inputs"].financial
                    project_cost = float(financial.estimated_project_cost or 0)
                    funding_gap = max(0.0, project_cost - float(context.available_capital) - float(context.funding_available))
                    funding_result = self.funding_service.recommend(
                        category=top["match"].profile.category,
                        project_cost=project_cost,
                        loan_amount=funding_gap if funding_gap > 0 else None,
                        limit=5,
                    )
                    top["funding"] = funding_result

                    # Generate next steps
                    top["next_steps"] = self.funding_service.generate_next_steps(
                        funding_result,
                        top.get("analysis")
                    )
                except Exception:
                    top = results[0]
                    top["funding"] = {"schemes": [], "loans": [], "available": False}
                    top["next_steps"] = []

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
        combined = (
            item.get("asuse_prediction") is not None
            or item.get("ises_context") is not None
        )
        if calibration is not None and calibration.model_used:
            return f"decision-engine-v3-combined+{calibration.model_version}" if combined else f"decision-engine-v1+{calibration.model_version}"
        return "decision-engine-v3-combined" if combined else "decision-engine-v1"
