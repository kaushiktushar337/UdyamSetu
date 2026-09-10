from pathlib import Path

from ml_engine.asuse_model import ASUSEProfitabilityModel, ASUSEPrediction, build_asuse_features
from ml_engine.decision_engine import BusinessAnalysisInput, calculate_business_analysis
from ml_engine.schemas import FinancialInput
from ml_engine.market_engine import MarketInput
from ml_engine.operational_engine import OperationalInput
from ml_engine.business_matcher import BusinessMatch
from ml_engine.profile_loader import BusinessProfileLoader
from ml_engine.recommendation_engine import RecommendationEngine, UserBusinessContext
from ml_engine.recommendation_pipeline import BusinessRecommendationPipeline

ROOT = Path(__file__).resolve().parents[1]


def _profiles():
    return BusinessProfileLoader.load_profiles_from_csv(
        str(ROOT / "seed_data" / "business_reference_profiles_database_ready.csv")
    )


def test_asuse_model_loads_and_predicts_from_udyamsetu_context():
    profile = next(p for p in _profiles() if "Bakery" in p.business_name)
    context = UserBusinessContext(
        available_capital=500000,
        interests="bakery food",
        skills="baking",
        experience_years=3,
        planned_workers=4,
        business_age_years=1,
        daily_work_hours=8,
    )
    generated = RecommendationEngine().generate_inputs(
        context,
        BusinessMatch(profile, 90, 95, 92.5, ["bakery"]),
    )
    model = ASUSEProfitabilityModel(ROOT / "models" / "asuse_profitability.joblib").load()
    prediction = model.predict(context, profile, generated)

    assert prediction.applicable is True
    assert prediction.profitability_tier in {"low", "medium", "high"}
    assert abs(sum(prediction.probabilities.values()) - 1.0) < 1e-5
    assert 0 <= prediction.viability_score <= 100
    assert "major_nic_2dig" in prediction.features


def test_asuse_overrides_are_used_exactly():
    profile = next(p for p in _profiles() if "Bakery" in p.business_name)
    context = UserBusinessContext(
        available_capital=500000,
        asuse_overrides={
            "district": 17,
            "location": 4,
            "major_nic_2dig": 10,
            "major_nic_5dig": 10799,
            "education_level": 6,
        },
    )
    features, inferred = build_asuse_features(context, profile)
    assert features["district"] == 17
    assert features["location"] == 4
    assert features["major_nic_5dig"] == 10799
    assert "major_nic_5dig" not in inferred


def test_pipeline_blends_asuse_score_into_decision_result():
    profile = next(p for p in _profiles() if "Bakery" in p.business_name)
    match = BusinessMatch(profile, 90, 95, 92.5, ["bakery"])

    class OneMatcher:
        def match(self, *args, **kwargs):
            return [match]

    model = ASUSEProfitabilityModel(ROOT / "models" / "asuse_profitability.joblib").load()
    pipeline = BusinessRecommendationPipeline([profile], matcher=OneMatcher(), asuse_model=model)
    result = pipeline.recommend(
        UserBusinessContext(
            available_capital=500000,
            interests="bakery",
            skills="baking",
            experience_years=3,
            planned_workers=4,
            business_age_years=1,
            daily_work_hours=8,
        ),
        top_k=1,
    )[0]

    assert result["asuse_prediction"].model_used is True
    assert result["analysis"].asuse_prediction is result["asuse_prediction"]
    assert result["final_recommendation_score"] == result["analysis"].overall_score
    assert "ASUSE" in result["analysis"].confidence


def test_out_of_scope_agriculture_profile_does_not_use_asuse_score():
    profile = next(p for p in _profiles() if "Mushroom" in p.business_name)
    context = UserBusinessContext(available_capital=500000, interests="mushroom", skills="farming")
    model = ASUSEProfitabilityModel(ROOT / "models" / "asuse_profitability.joblib").load()
    prediction = model.predict(context, profile)
    assert prediction.applicable is False
    assert prediction.viability_score is None
    assert prediction.probabilities == {}


def _analysis_input():
    return BusinessAnalysisInput(
        financial=FinancialInput(available_capital=500000, estimated_project_cost=300000, estimated_monthly_revenue=150000, estimated_monthly_expenses=100000),
        market=MarketInput(demand_score=75, competition_score=40, opportunity_score=70, pricing_score=60),
        operational=OperationalInput(resource_score=80, infrastructure_score=70, supply_chain_score=65, logistics_score=60),
        business_risks=[],
    )


def test_integrated_analysis_has_explainable_score_breakdown():
    result = calculate_business_analysis(
        _analysis_input(),
        asuse_prediction=ASUSEPrediction(
            applicable=True,
            profitability_tier="high",
            probabilities={"low": 0.05, "medium": 0.15, "high": 0.80},
            viability_score=83.0,
            model_version="test-model",
            model_path="test.joblib",
            inferred_features=("major_nic_5dig",),
            reason="test",
        ),
    )
    explanation = result.explanation
    assert explanation["decision"] == result.decision
    assert explanation["overall_score"] == result.overall_score
    assert set(("financial", "market", "operational", "risk", "asuse")).issubset(explanation["score_components"])
    assert set(("financial", "market", "operational", "risk", "asuse")).issubset(explanation["score_contributions"])
    assert explanation["asuse"]["tier"] == "high"
    assert "major_nic_5dig" in explanation["asuse"]["inferred_features"]
