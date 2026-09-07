from .schemas import FinancialInput, FinancialResult


def clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))


def calculate_financial_feasibility(data: FinancialInput) -> FinancialResult:
    total_available = max(0.0, data.available_capital) + max(0.0, data.funding_available)
    project_cost = max(0.0, data.estimated_project_cost)

    # 1. Capital coverage
    if project_cost == 0:
        coverage_ratio = 1.0
    else:
        coverage_ratio = total_available / project_cost

    funding_gap = max(0.0, project_cost - total_available)

    # 2. Monthly profitability
    monthly_profit = data.estimated_monthly_revenue - data.estimated_monthly_expenses

    if data.estimated_monthly_revenue > 0:
        profit_margin = (monthly_profit / data.estimated_monthly_revenue) * 100
    else:
        profit_margin = 0.0

    # 3. Simple break-even estimate
    # If startup cost is fully known and monthly profit is positive,
    # estimate months required to recover project cost.
    if monthly_profit > 0 and project_cost > 0:
        break_even_months = round(project_cost / monthly_profit, 1)
    else:
        break_even_months = None

    # 4. Explainable component scores
    # Capital score rewards adequate funding but does not reward excess capital above 100%.
    capital_score = clamp(coverage_ratio * 100)

    # Margin score:
    # 20%+ margin is treated as strong for this initial prototype.
    margin_score = clamp((profit_margin / 20.0) * 100)

    # Break-even score:
    # Faster break-even receives a higher score.
    if break_even_months is None:
        break_even_score = 0.0
    elif break_even_months <= 12:
        break_even_score = 100.0
    elif break_even_months <= 24:
        break_even_score = 75.0
    elif break_even_months <= 36:
        break_even_score = 50.0
    elif break_even_months <= 60:
        break_even_score = 25.0
    else:
        break_even_score = 10.0

    # Final weighted financial score
    financial_score = round(
        capital_score * 0.45 +
        margin_score * 0.35 +
        break_even_score * 0.20,
        2
    )

    # 5. Human-readable rating
    if financial_score >= 80:
        rating = "Strong"
    elif financial_score >= 65:
        rating = "Good"
    elif financial_score >= 45:
        rating = "Moderate"
    else:
        rating = "Weak"

    # 6. Recommendations
    recommendations = []

    if coverage_ratio < 1:
        recommendations.append(
            f"Current funding has a gap of ₹{funding_gap:,.0f}. Consider reducing startup scale or arranging additional funding."
        )
    else:
        recommendations.append("Available capital is sufficient to cover the estimated startup cost.")

    if monthly_profit <= 0:
        recommendations.append(
            "The estimated monthly operation is not profitable. Revenue or expense assumptions should be revised."
        )
    elif profit_margin < 10:
        recommendations.append(
            "Profit margin is low. Focus on reducing operating costs or improving pricing."
        )
    elif profit_margin >= 20:
        recommendations.append(
            "The estimated profit margin is strong under the current assumptions."
        )

    if break_even_months is None:
        recommendations.append(
            "A break-even period cannot currently be estimated because projected monthly profit is not positive."
        )
    elif break_even_months > 36:
        recommendations.append(
            "The projected break-even period is long. Consider lowering startup costs or increasing expected revenue."
        )
    else:
        recommendations.append(
            f"Estimated break-even period: approximately {break_even_months} months."
        )

    return FinancialResult(
        capital_coverage_ratio=round(coverage_ratio, 3),
        funding_gap=round(funding_gap, 2),
        monthly_profit=round(monthly_profit, 2),
        profit_margin=round(profit_margin, 2),
        estimated_break_even_months=break_even_months,
        financial_score=financial_score,
        rating=rating,
        recommendations=recommendations,
    )
