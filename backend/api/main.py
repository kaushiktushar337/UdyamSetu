from __future__ import annotations

import os
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any
from uuid import UUID

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

from chatbot.chat_service import ChatService
from chatbot.conversation_manager import ConversationManager
from chatbot.schemas import ChatRequest as BotChatRequest
from ml_engine.decision_service import UdyamSetuDecisionService
from ml_engine.recommendation_engine import UserBusinessContext
from ml_engine.profile_loader import BusinessProfileLoader
from ml_engine.location_metrics_loader import LocationMetricsLoader
from ml_engine.recommendation_pipeline import BusinessRecommendationPipeline
from ml_engine.asuse_model import ASUSEProfitabilityModel
from ml_engine.funding_service import FundingService
from ml_engine.analysis_repository import AnalysisRepository
from .insights_service import InsightsService
from .location_service import LocationService
from .schemas import AnalyzeRequest, AnalyzeResponse
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env')
DEFAULT_PROFILE_CSV = ROOT / "seed_data" / "business_reference_profiles_database_ready.csv"
DEFAULT_MODEL_PATH = ROOT / "models" / "asuse_profitability.joblib"


def _jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return {k: _jsonable(v) for k, v in asdict(value).items()}
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return value


def build_service() -> UdyamSetuDecisionService:
    database_url = os.getenv("DATABASE_URL")
    model_path = os.getenv("ASUSE_MODEL_PATH", str(DEFAULT_MODEL_PATH))
    asuse_model = None
    if model_path and Path(model_path).exists():
        asuse_model = ASUSEProfitabilityModel(model_path).load()

    if database_url:
        profiles = BusinessProfileLoader(database_url).load_profiles()
        location_loader = LocationMetricsLoader(database_url)
        repository = AnalysisRepository(database_url)
    else:
        profiles = BusinessProfileLoader.load_profiles_from_csv(str(DEFAULT_PROFILE_CSV))
        location_loader = None
        repository = None

    pipeline = BusinessRecommendationPipeline(profiles=profiles, location_loader=location_loader, asuse_model=asuse_model)
    return UdyamSetuDecisionService(pipeline, repository)


class LocationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    user_id: str | None = None
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    accuracy: float | None = Field(default=None, ge=0)


class ChatApiRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = None
    user_id: str | None = None
    location_text: str | None = None


class FundingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    category: str | None = None
    project_cost: float | None = Field(default=None, ge=0)
    loan_amount: float | None = Field(default=None, ge=0)
    state: str | None = None
    district: str | None = None
    age: int | None = Field(default=None, ge=0)
    credit_score: int | None = Field(default=None, ge=0)
    business_vintage_months: int | None = Field(default=None, ge=0)
    limit: int = Field(default=5, ge=1, le=20)


class InsightRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    location_id: str | None = None
    state: str | None = None
    district: str | None = None
    category: str = "Dairy"


def create_app(service: UdyamSetuDecisionService | None = None) -> FastAPI:
    app = FastAPI(title="UdyamSetu API", version="2.0.0")
    origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "*").split(",") if x.strip()]
    app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=origins != ["*"], allow_methods=["*"], allow_headers=["*"])
    app.state.decision_service = service
    app.state.chat_service = None

    def get_service():
        if app.state.decision_service is None:
            try:
                app.state.decision_service = build_service()
            except Exception as exc:
                raise HTTPException(status_code=503, detail=f"Decision engine unavailable: {exc}") from exc
        return app.state.decision_service

    def get_chat_service():
        if app.state.chat_service is None:
            app.state.chat_service = ChatService(memory=ConversationManager(database_url=os.getenv("DATABASE_URL")), funding_provider=FundingService())
        return app.state.chat_service

    @app.get("/health")
    def health():
        svc = app.state.decision_service
        return {"status": "ok", "service": "udyamsetu", "loaded": svc is not None, "asuse_model_loaded": bool(svc is not None and getattr(svc.pipeline.asuse_model, "is_loaded", False))}

    @app.post("/api/chat")
    def chat(request: ChatApiRequest):
        try:
            result = get_chat_service().chat(BotChatRequest(message=request.message, conversation_id=request.conversation_id, user_id=request.user_id, location_text=request.location_text))
            return _jsonable(result)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Chat service unavailable: {exc}") from exc

    @app.get("/api/chat/history/{conversation_id}")
    def chat_history(conversation_id: str):
        try:
            history = get_chat_service().memory.get_history(conversation_id)
            return {"conversation_id": conversation_id, "messages": history}
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"History unavailable: {exc}") from exc

    @app.post("/api/location")
    def save_location(request: LocationRequest):
        location_service = LocationService()
        resolution = location_service.resolve(request.latitude, request.longitude)
        persisted = location_service.save_capture(request.user_id, request.latitude, request.longitude, request.accuracy, resolution)
        # Deliberately never return raw GPS coordinates.
        return {**resolution, "persisted": persisted}

    @app.get("/api/location/latest/{user_id}")
    def latest_location(user_id: str):
        result = LocationService().latest(user_id)
        if not result:
            raise HTTPException(status_code=404, detail="No saved location found")
        return result

    @app.get("/api/locations")
    def locations():
        try:
            return {"locations": InsightsService().locations()}
        except Exception as exc:
            raise HTTPException(status_code=503, detail=f"Locations unavailable: {exc}") from exc

    @app.post("/api/funding/recommendations")
    def funding_recommendations(request: FundingRequest):
        try:
            return FundingService().recommend(
                category=request.category, project_cost=request.project_cost, loan_amount=request.loan_amount,
                state=request.state, district=request.district, age=request.age, credit_score=request.credit_score,
                business_vintage_months=request.business_vintage_months, limit=request.limit,
            )
        except Exception as exc:
            raise HTTPException(status_code=503, detail=f"Funding recommendations unavailable: {exc}") from exc

    @app.get("/api/funding/schemes")
    def funding_schemes(category: str | None = None, project_cost: float | None = None, limit: int = 10):
        try:
            return {"schemes": FundingService().list_schemes(project_cost=project_cost, category=category, limit=min(limit, 20))}
        except Exception as exc:
            raise HTTPException(status_code=503, detail=f"Schemes unavailable: {exc}") from exc

    @app.get("/api/funding/loans")
    def funding_loans(category: str | None = None, loan_amount: float | None = None, state: str | None = None, district: str | None = None, limit: int = 10):
        try:
            return {"loans": FundingService().list_loans(category=category, loan_amount=loan_amount, state=state, district=district, limit=min(limit, 20))}
        except Exception as exc:
            raise HTTPException(status_code=503, detail=f"Loan plans unavailable: {exc}") from exc

    @app.post("/api/insights")
    def insights(request: InsightRequest):
        try:
            location_id = request.location_id
            if not location_id:
                matches = [x for x in InsightsService().locations() if (not request.state or x["state"] == request.state) and (not request.district or x["district"] == request.district)]
                if matches:
                    location_id = matches[0]["location_id"]
            if not location_id:
                raise HTTPException(status_code=404, detail="Select a supported location or share your current location")
            insight_data = InsightsService().by_location(location_id, request.category)
            if insight_data.get("available"):
                try:
                    svc = get_service()
                    ml_matches = svc.pipeline.matcher.match(
                        f"Business category: {request.category}",
                        available_capital=None,
                        top_k=5,
                    )
                    insight_data["ml_business_matches"] = [
                        {
                            "business_name": m.profile.business_name,
                            "subcategory": m.profile.subcategory,
                            "semantic_score": m.semantic_score,
                        }
                        for m in ml_matches
                    ]
                except Exception:
                    insight_data["ml_business_matches"] = []
            return insight_data
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=503, detail=f"Insights unavailable: {exc}") from exc

    @app.post("/api/analyze", response_model=AnalyzeResponse)
    def analyze(request: AnalyzeRequest):
        svc = get_service()
        context = UserBusinessContext(
            available_capital=request.available_capital, funding_available=request.funding_available,
            interests=request.interests, skills=request.skills, experience_years=request.experience_years,
            available_resources=request.available_resources, infrastructure=request.infrastructure,
            location=request.location, location_id=request.location_id, preferences=request.preferences,
            asuse_overrides=request.asuse_overrides, planned_workers=request.planned_workers,
            business_age_years=request.business_age_years, daily_work_hours=request.daily_work_hours,
        )
        try:
            results = svc.recommend(context, top_k=request.top_k)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc
        if not results:
            raise HTTPException(status_code=404, detail="No matching business profiles found")
        item = results[0]
        analysis = item["analysis"]
        explanation = analysis.explanation or {}
        match = item["match"]
        profile = match.profile
        prediction = item.get("asuse_prediction")
        analysis_id = None
        persisted = False
        if request.persist:
            if not (request.user_id and request.business_id and request.location_id):
                raise HTTPException(status_code=400, detail="user_id, business_id and location_id are required when persist=true")
            try:
                analysis_id = svc.persist_result(item, user_id=request.user_id, business_id=request.business_id, location_id=request.location_id)
                persisted = True
            except Exception as exc:
                raise HTTPException(status_code=500, detail=f"Analysis persistence failed: {exc}") from exc
        return AnalyzeResponse(
            analysis_id=analysis_id,
            business={"profile_id": profile.profile_id, "business_name": profile.business_name, "category": profile.category, "subcategory": profile.subcategory},
            decision={"decision": analysis.decision, "overall_score": analysis.overall_score, "confidence": item.get("confidence"), "confidence_type": "data-quality confidence, not success probability"},
            scores={"components": explanation.get("score_components", {}), "contributions": explanation.get("score_contributions", {}), "weights": explanation.get("weights", {})},
            asuse=_jsonable(prediction), funding=_jsonable(item.get("funding")), strengths=explanation.get("strengths", []), concerns=explanation.get("concerns", []), recommendations=analysis.recommendations,
            match={"semantic_score": match.semantic_score, "capital_score": match.capital_score, "final_score": match.final_score, "reasons": match.reasons},
            engine_version=svc.engine_version(item), persisted=persisted,
        )

    @app.get("/api/recommendations")
    def recommendations(request: AnalyzeRequest):
        svc = get_service()
        context = UserBusinessContext(
            available_capital=request.available_capital, funding_available=request.funding_available,
            interests=request.interests, skills=request.skills, experience_years=request.experience_years,
            available_resources=request.available_resources, infrastructure=request.infrastructure,
            location=request.location, location_id=request.location_id, preferences=request.preferences,
            asuse_overrides=request.asuse_overrides, planned_workers=request.planned_workers,
            business_age_years=request.business_age_years, daily_work_hours=request.daily_work_hours,
        )
        try:
            results = svc.recommend(context, top_k=request.top_k)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Recommendation failed: {exc}") from exc
        return {"recommendations": [{"profile_id": item["profile_id"], "business_name": item["business_name"], "score": item["final_recommendation_score"], "decision": item["analysis"].decision, "confidence": item.get("confidence"), "asuse": _jsonable(item.get("asuse_prediction")), "explanation": item["analysis"].explanation} for item in results]}

    return app


app = create_app()
