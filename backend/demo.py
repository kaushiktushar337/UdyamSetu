from ml_engine.schemas import FinancialInput
from ml_engine.financial_engine import calculate_financial_feasibility


def run_demo(name, data):
    result = calculate_financial_feasibility(data)

    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)
    print(f"Capital coverage: {result.capital_coverage_ratio * 100:.1f}%")
    print(f"Funding gap: ₹{result.funding_gap:,.0f}")
    print(f"Monthly profit: ₹{result.monthly_profit:,.0f}")
    print(f"Profit margin: {result.profit_margin:.1f}%")
    print(f"Break-even: {result.estimated_break_even_months} months")
    print(f"Financial score: {result.financial_score}/100")
    print(f"Rating: {result.rating}")
    print("Recommendations:")
    for recommendation in result.recommendations:
        print(f"- {recommendation}")


run_demo(
    "Scenario 1: Small Dairy Business",
    FinancialInput(
        available_capital=200000,
        estimated_project_cost=300000,
        estimated_monthly_revenue=70000,
        estimated_monthly_expenses=50000,
    )
)

run_demo(
    "Scenario 2: Well Funded Business",
    FinancialInput(
        available_capital=500000,
        estimated_project_cost=350000,
        estimated_monthly_revenue=100000,
        estimated_monthly_expenses=70000,
    )
)

run_demo(
    "Scenario 3: Financially Weak Business",
    FinancialInput(
        available_capital=100000,
        estimated_project_cost=400000,
        estimated_monthly_revenue=50000,
        estimated_monthly_expenses=55000,
    )
)


from ml_engine.market_engine import MarketInput, calculate_market_feasibility


def run_market_demo(name, data):
    result = calculate_market_feasibility(data)

    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)
    print(f"Demand score: {data.demand_score}/100")
    print(f"Competition score: {data.competition_score}/100")
    print(f"Opportunity score: {data.opportunity_score}/100")
    print(f"Pricing score: {data.pricing_score}/100")
    print(f"Market score: {result.market_score}/100")
    print(f"Rating: {result.rating}")
    print("Recommendations:")
    for recommendation in result.recommendations:
        print(f"- {recommendation}")


run_market_demo(
    "Market Scenario 1: Promising Local Market",
    MarketInput(
        demand_score=80,
        competition_score=35,
        opportunity_score=78,
        pricing_score=70,
    )
)

run_market_demo(
    "Market Scenario 2: Highly Competitive Market",
    MarketInput(
        demand_score=85,
        competition_score=85,
        opportunity_score=55,
        pricing_score=60,
    )
)

run_market_demo(
    "Market Scenario 3: Weak Market",
    MarketInput(
        demand_score=30,
        competition_score=70,
        opportunity_score=25,
        pricing_score=35,
    )
)
