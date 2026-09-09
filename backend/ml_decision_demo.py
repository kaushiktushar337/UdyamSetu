from pathlib import Path
from ml_engine.profile_loader import BusinessProfileLoader
from ml_engine.recommendation_engine import UserBusinessContext
from ml_engine.recommendation_pipeline import BusinessRecommendationPipeline

ROOT = Path(__file__).resolve().parent
profiles = BusinessProfileLoader.load_profiles_from_csv(
    str(ROOT / "seed_data" / "business_reference_profiles_database_ready.csv")
)
pipeline = BusinessRecommendationPipeline(profiles)

context = UserBusinessContext(
    available_capital=300000,
    interests="food processing bakery dairy products",
    skills="food preparation bakery business management",
    experience_years=2,
    available_resources=["supplier", "packaging"],
    infrastructure=["500 sq ft shed", "oven", "delivery vehicle"],
    location="India",
    preferences="small scalable business",
)

results = pipeline.recommend(context, top_k=3, location_metrics={
    "demand_score": 75,
    "competition_score": 45,
    "opportunity_score": 70,
})

print("UDYAMSETU ML DECISION ENGINE")
print("=" * 60)
for i, item in enumerate(results, 1):
    analysis = item["analysis"]
    match = item["match"]
    print(f"#{i} {item['business_name']}")
    print(f"  Match score: {match.final_score}/100")
    print(f"  Decision score: {analysis.overall_score}/100")
    print(f"  Final recommendation score: {item['final_recommendation_score']}/100")
    print(f"  Decision: {analysis.decision}")
    print(f"  Financial/Market/Operational/Risk feasibility: "
          f"{analysis.financial.financial_score}/"
          f"{analysis.market.market_score}/"
          f"{analysis.operational.operational_score}/"
          f"{analysis.risk.feasibility_risk_score}")
    print()
