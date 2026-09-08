from ml_engine.profile_loader import BusinessProfileLoader
from ml_engine.recommendation_engine import UserBusinessContext
from ml_engine.recommendation_pipeline import BusinessRecommendationPipeline

profiles = BusinessProfileLoader().load_profiles()
pipeline = BusinessRecommendationPipeline(profiles)

context = UserBusinessContext(
    available_capital=500000,
    interests="food processing, agriculture products and local manufacturing",
    skills="basic food preparation and small business management",
    experience_years=2,
    available_resources=["local suppliers"],
    infrastructure=["small workspace"],
    location="India",
)

results = pipeline.recommend(context, top_k=5)

for i, item in enumerate(results, 1):
    match = item["match"]
    analysis = item["analysis"]

    print(f"\n{i}. {item['business_name']}")
    print(f"Overall feasibility score: {analysis.overall_score}/100")
    print(f"Decision: {analysis.decision}")
    print(f"Business match score: {match.final_score}/100")
    print(f"Financial score: {analysis.financial.financial_score}/100")
    print(f"Market score: {analysis.market.market_score}/100")
    print(f"Operational score: {analysis.operational.operational_score}/100")
    print(f"Risk feasibility score: {analysis.risk.feasibility_risk_score}/100")

    if item["generated_inputs"].explanation["data_gaps"]:
        print("Data gaps:", ", ".join(item["generated_inputs"].explanation["data_gaps"]))
