from ml_engine.schemas import FinancialInput
from ml_engine.market_engine import MarketInput
from ml_engine.operational_engine import OperationalInput
from ml_engine.risk_engine import RiskItem
from ml_engine.decision_engine import BusinessAnalysisInput, calculate_business_analysis, result_for_database

scenario = BusinessAnalysisInput(
    financial=FinancialInput(
        available_capital=200000,
        estimated_project_cost=300000,
        estimated_monthly_revenue=70000,
        estimated_monthly_expenses=50000,
    ),
    market=MarketInput(
        demand_score=78,
        competition_score=55,
        opportunity_score=72,
        pricing_score=65,
    ),
    operational=OperationalInput(
        resource_score=75,
        infrastructure_score=65,
        supply_chain_score=70,
        logistics_score=60,
    ),
    business_risks=[
        RiskItem(
            risk_type="Seasonal",
            risk_score=45,
            description="Demand may fluctuate during some periods.",
            mitigation="Maintain multiple customer segments and manage inventory carefully.",
        )
    ],
)

result = calculate_business_analysis(scenario)

print("=" * 60)
print("UDYAMSETU COMPLETE BUSINESS ANALYSIS")
print("=" * 60)
print(f"Overall score: {result.overall_score}/100")
print(f"Decision: {result.decision}")
print(f"Financial: {result.financial.financial_score}/100 ({result.financial.rating})")
print(f"Market: {result.market.market_score}/100 ({result.market.rating})")
print(f"Operational: {result.operational.operational_score}/100 ({result.operational.rating})")
print(f"Risk feasibility: {result.risk.feasibility_risk_score}/100 ({result.risk.severity} risk)")
print("\nRecommendations:")
for item in result.recommendations:
    print("-", item)

print("\nDatabase payload sections:")
for table_name in result_for_database(result):
    print("-", table_name)
