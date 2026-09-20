import sys
import types
sys.modules.setdefault('psycopg2', types.ModuleType('psycopg2'))

import unittest

from api.insights_service import (
    aggregate_metric_rows,
    canonical_category,
    combine_opportunity,
    local_environment_score,
    normalize_score,
)


class TestBusinessInsights(unittest.TestCase):
    def test_category_aliases(self):
        self.assertEqual(canonical_category("Dairy"), "Agriculture Allied")
        self.assertEqual(canonical_category("Textiles"), "Manufacturing")
        self.assertEqual(canonical_category("Food Processing"), "Food Processing")

    def test_scores_are_not_silently_clamped(self):
        self.assertEqual(normalize_score(57), 57)
        self.assertEqual(normalize_score(0.57), 0.57)
        self.assertIsNone(normalize_score(5700))
        self.assertIsNone(normalize_score("bad"))

    def test_environment_score_is_bounded(self):
        score = local_environment_score({
            "profit_business_pct": 80,
            "bank_account_pct": 70,
            "business_loan_pct": 40,
            "competitor_monitoring_pct": 60,
            "customer_feedback_pct": 80,
            "monthly_budget_pct": 50,
            "sales_target_pct": 70,
            "electricity_use_pct": 90,
            "power_outage_pct": 10,
        })
        self.assertEqual(score, 71.5)
        self.assertTrue(0 <= score <= 100)

    def test_environment_score_handles_missing_values(self):
        self.assertEqual(local_environment_score({"profit_business_pct": 75}), 75)

    def test_opportunity_blend(self):
        self.assertEqual(combine_opportunity(80, 60), 75)
        self.assertEqual(combine_opportunity(80, None), 80)
        self.assertEqual(combine_opportunity(None, 60), 60)
        self.assertIsNone(combine_opportunity(None, None))

    def test_aggregate_is_one_row_per_subcategory(self):
        rows = [
            {"subcategory": "Bakery", "competition_count": 500, "data_source": "Verified local market dataset", "demand_score": 72, "competition_score": 35, "opportunity_score": 80, "average_market_price": None, "data_date": "2024-03-31"},
            {"subcategory": "Pickles", "competition_count": 450, "data_source": "Verified local market dataset", "demand_score": 70, "competition_score": 36, "opportunity_score": 78, "average_market_price": 200.834, "data_date": "2024-03-31"},
            {"subcategory": "Spice Processing", "competition_count": 300, "data_source": "Verified local market dataset", "demand_score": 69, "competition_score": 40, "opportunity_score": 75, "average_market_price": 201, "data_date": "2024-03-31"},
        ]
        result = aggregate_metric_rows(rows)
        self.assertEqual(result["competition_count"], 1250)
        self.assertEqual(result["metric_rows"], 3)
        self.assertEqual(result["average_market_price"], 200.9)
        self.assertEqual(result["demand_score"], 70.56)

    def test_duplicate_join_cannot_multiply_count(self):
        # This is the regression case: the same metric must never be counted
        # once for every matching business-reference profile.
        rows = [
            {"subcategory": "Fruit Processing", "competition_count": 100, "data_source": "Verified local market dataset", "demand_score": 60, "competition_score": 40, "opportunity_score": 70, "average_market_price": None, "data_date": "2024-03-31"},
            {"subcategory": "Pickles", "competition_count": 50, "data_source": "Verified local market dataset", "demand_score": 65, "competition_score": 35, "opportunity_score": 72, "average_market_price": None, "data_date": "2024-03-31"},
        ]
        result = aggregate_metric_rows(rows)
        self.assertEqual(result["competition_count"], 150)
        self.assertNotEqual(result["competition_count"], 21066374)


    def test_unverified_asuse_counts_are_not_summed(self):
        rows = [
            {"subcategory": "Bakery", "competition_count": 1755428, "data_source": "ASUSE 2023-24 profile-aligned proxy", "demand_score": 50, "competition_score": 50, "opportunity_score": 50, "average_market_price": None, "data_date": "2024-03-31"},
            {"subcategory": "Food products", "competition_count": 1403868, "data_source": "ASUSE 2023-24 derived", "demand_score": 50, "competition_score": 50, "opportunity_score": 50, "average_market_price": None, "data_date": "2024-03-31"},
            {"subcategory": "Other", "competition_count": 3455954, "data_source": "ASUSE 2023-24 derived", "demand_score": 50, "competition_score": 50, "opportunity_score": 50, "average_market_price": None, "data_date": "2024-03-31"},
        ]
        result = aggregate_metric_rows(rows)
        self.assertIsNone(result["competition_count"])
        self.assertNotEqual(result["competition_count"], 21066374)


    def test_ises_sector_count_can_fill_missing_local_count(self):
        rows = [
            {"subcategory": "Bakery", "competition_count": 1755428, "data_source": "ASUSE 2023-24 profile-aligned proxy", "demand_score": 50, "competition_score": 50, "opportunity_score": 50, "average_market_price": None, "data_date": "2024-03-31"},
            {"subcategory": "Pickles", "competition_count": 1755428, "data_source": "ASUSE 2023-24 profile-aligned proxy", "demand_score": 50, "competition_score": 50, "opportunity_score": 50, "average_market_price": None, "data_date": "2024-03-31"},
        ]
        result = aggregate_metric_rows(rows, fallback_competition_count=1364.88)
        self.assertEqual(result["competition_count"], 1365)

    def test_verified_local_counts_are_additive(self):
        rows = [
            {"subcategory": "Bakery", "competition_count": 118, "data_source": "Verified local market dataset", "demand_score": 60, "competition_score": 40, "opportunity_score": 70, "average_market_price": None, "data_date": "2026-09-19"},
            {"subcategory": "Pickles", "competition_count": 100, "data_source": "Verified local market dataset", "demand_score": 65, "competition_score": 35, "opportunity_score": 72, "average_market_price": None, "data_date": "2026-09-19"},
        ]
        result = aggregate_metric_rows(rows)
        self.assertEqual(result["competition_count"], 218)

    def test_synthetic_local_counts_are_used_and_additive(self):
        # Synthetic prototype metrics are intentionally location-specific
        # development market data. They are valid for the synthetic Business
        # Insights experience and must not be discarded in favor of national
        # ASUSE reference/population values.
        rows = [
            {"subcategory": "Bakery", "competition_count": 118, "data_source": "UdyamSetu synthetic prototype dataset", "demand_score": 62, "competition_score": 42, "opportunity_score": 60, "average_market_price": None, "data_date": "2026-09-19"},
            {"subcategory": "Flour Milling", "competition_count": 121, "data_source": "UdyamSetu synthetic prototype dataset", "demand_score": 62, "competition_score": 42, "opportunity_score": 60, "average_market_price": None, "data_date": "2026-09-19"},
            {"subcategory": "Fruit Processing", "competition_count": 334, "data_source": "UdyamSetu synthetic prototype dataset", "demand_score": 62, "competition_score": 42, "opportunity_score": 60, "average_market_price": None, "data_date": "2026-09-19"},
            {"subcategory": "Millet Foods", "competition_count": 244, "data_source": "UdyamSetu synthetic prototype dataset", "demand_score": 62, "competition_score": 42, "opportunity_score": 60, "average_market_price": None, "data_date": "2026-09-19"},
            {"subcategory": "Millet Processing", "competition_count": 104, "data_source": "UdyamSetu synthetic prototype dataset", "demand_score": 62, "competition_score": 42, "opportunity_score": 60, "average_market_price": None, "data_date": "2026-09-19"},
            {"subcategory": "Pickles", "competition_count": 100, "data_source": "UdyamSetu synthetic prototype dataset", "demand_score": 62, "competition_score": 42, "opportunity_score": 60, "average_market_price": None, "data_date": "2026-09-19"},
            {"subcategory": "Spice Processing", "competition_count": 111, "data_source": "UdyamSetu synthetic prototype dataset", "demand_score": 62, "competition_score": 42, "opportunity_score": 60, "average_market_price": None, "data_date": "2026-09-19"},
            {"subcategory": "Traditional Snacks", "competition_count": 107, "data_source": "UdyamSetu synthetic prototype dataset", "demand_score": 62, "competition_score": 42, "opportunity_score": 60, "average_market_price": None, "data_date": "2026-09-19"},
        ]
        result = aggregate_metric_rows(rows)
        self.assertEqual(result["competition_count"], 1239)

    def test_missing_price_stays_null(self):
        result = aggregate_metric_rows([
            {"subcategory": "Bakery", "competition_count": 100, "demand_score": 60, "competition_score": 40, "opportunity_score": 70, "average_market_price": None, "data_date": "2024-03-31"},
        ])
        self.assertIsNone(result["average_market_price"])


if __name__ == "__main__":
    unittest.main()
