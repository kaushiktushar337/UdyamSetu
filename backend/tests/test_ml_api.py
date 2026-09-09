from pathlib import Path

from fastapi.testclient import TestClient

from api.main import create_app
from ml_engine.business_matcher import BusinessMatch
from ml_engine.decision_service import UdyamSetuDecisionService
from ml_engine.recommendation_engine import RecommendationEngine, UserBusinessContext
from ml_engine.recommendation_pipeline import BusinessRecommendationPipeline
from ml_engine.profile_loader import BusinessProfileLoader
from ml_engine.asuse_model import ASUSEProfitabilityModel

ROOT = Path(__file__).resolve().parents[1]


def _service():
    profiles = BusinessProfileLoader.load_profiles_from_csv(
        str(ROOT / "seed_data" / "business_reference_profiles_database_ready.csv")
    )
    profile = next(p for p in profiles if "Bakery" in p.business_name)
    match = BusinessMatch(profile, 90.0, 95.0, 91.25, ["test"])

    class OneMatcher:
        def match(self, *args, **kwargs):
            return [match]

    model = ASUSEProfitabilityModel(ROOT / "models" / "asuse_profitability.joblib").load()
    pipeline = BusinessRecommendationPipeline(profiles=[profile], matcher=OneMatcher(), asuse_model=model)
    return UdyamSetuDecisionService(pipeline)


def test_health():
    client = TestClient(create_app(_service()))
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["asuse_model_loaded"] is True


def test_analyze_returns_frontend_ready_contract():
    client = TestClient(create_app(_service()))
    response = client.post(
        "/api/analyze",
        json={
            "available_capital": 500000,
            "interests": "bakery food",
            "skills": "baking",
            "experience_years": 3,
            "planned_workers": 4,
            "business_age_years": 1,
            "daily_work_hours": 8,
            "top_k": 1,
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["business"]["business_name"]
    assert body["decision"]["decision"] in {"Highly Viable", "Viable", "Needs Modification", "Reconsider"}
    assert 0 <= body["decision"]["overall_score"] <= 100
    assert "components" in body["scores"]
    assert "asuse" in body
    assert body["asuse"]["profitability_tier"] in {"low", "medium", "high"}
    assert isinstance(body["strengths"], list)
    assert isinstance(body["recommendations"], list)


def test_analyze_requires_business_context():
    client = TestClient(create_app(_service()))
    response = client.post("/api/analyze", json={"available_capital": 500000})
    assert response.status_code == 422
