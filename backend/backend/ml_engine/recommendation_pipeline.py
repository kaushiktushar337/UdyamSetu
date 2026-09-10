"""End-to-end recommendation pipeline with optional learnable calibration."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from .business_matcher import BusinessMatcher, build_user_business_query
from .profile_loader import BusinessProfile
from .recommendation_engine import RecommendationEngine, UserBusinessContext
from .decision_engine import BusinessAnalysisInput, calculate_business_analysis
from .feature_extractor import FeatureExtractor
from .calibration_model import ScoreCalibrator
from .asuse_model import ASUSEProfitabilityModel


class BusinessRecommendationPipeline:
    def __init__(
        self,
        profiles: List[BusinessProfile],
        calibrator: Optional[ScoreCalibrator] = None,
        location_loader=None,
        matcher=None,
        asuse_model: Optional[ASUSEProfitabilityModel] = None,
    ):
        self.matcher = matcher or BusinessMatcher().fit(profiles)
        self.recommendation_engine = RecommendationEngine()
        self.feature_extractor = FeatureExtractor()
        self.calibrator = calibrator or ScoreCalibrator()
        self.location_loader = location_loader
        self.asuse_model = asuse_model

    def _resolve_location_metrics(self, context, profile, supplied):
        if supplied is not None:
            return supplied
        if self.location_loader is None or not context.location_id:
            return None
        return self.location_loader.get_metrics(
            context.location_id, profile.category or "", profile.subcategory
        )

    def recommend(self, context: UserBusinessContext, top_k: int = 5, location_metrics: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        query = build_user_business_query(
            interests=context.interests,
            skills=context.skills,
            preferences=context.preferences,
            location_context=context.location,
        )
        matches = self.matcher.match(
            query,
            available_capital=context.available_capital + context.funding_available,
            top_k=top_k,
        )
        results: List[Dict[str, Any]] = []
        for match in matches:
            resolved_metrics = self._resolve_location_metrics(context, match.profile, location_metrics)
            generated = self.recommendation_engine.generate_inputs(context, match, resolved_metrics)
            analysis_input = BusinessAnalysisInput(
                financial=generated.financial,
                market=generated.market,
                operational=generated.operational,
                business_risks=generated.business_risks,
            )
            asuse_prediction = None
            if self.asuse_model is not None:
                asuse_prediction = self.asuse_model.predict(context, match.profile, generated)
            analysis = calculate_business_analysis(analysis_input, asuse_prediction=asuse_prediction)
            features = self.feature_extractor.extract(context, match, generated, analysis)
            calibration = self.calibrator.predict(features, analysis.overall_score)
            results.append({
                "profile_id": match.profile.profile_id,
                "business_name": match.profile.business_name,
                "match": match,
                "generated_inputs": generated,
                "analysis_input": analysis_input,
                "analysis": analysis,
                "features": features,
                "calibration": calibration,
                "asuse_prediction": asuse_prediction,
                "final_recommendation_score": analysis.overall_score,
                "explanation": analysis.explanation,
            })
        results.sort(key=lambda item: (item["final_recommendation_score"], item["match"].final_score), reverse=True)
        return results
