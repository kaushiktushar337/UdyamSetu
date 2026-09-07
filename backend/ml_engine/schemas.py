from dataclasses import dataclass
from typing import List, Optional

@dataclass
class FinancialInput:
    available_capital: float
    estimated_project_cost: float
    estimated_monthly_revenue: float
    estimated_monthly_expenses: float
    funding_available: float = 0.0

@dataclass
class FinancialResult:
    capital_coverage_ratio: float
    funding_gap: float
    monthly_profit: float
    profit_margin: float
    estimated_break_even_months: Optional[float]
    financial_score: float
    rating: str
    recommendations: List[str]
