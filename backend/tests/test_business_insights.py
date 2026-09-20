import sys
import types
import unittest

# The source package requires psycopg2 in production. Stub it here so the
# pure scoring/aggregation tests can run in this lightweight test container.
sys.modules.setdefault("psycopg2", types.ModuleType("psycopg2"))

from api import insights_service
from api.insights_service import (
    InsightsService,
    canonical_category,
    combine_opportunity,
    local_environment_score,
)


class FakeCursor:
    def __init__(self):
        self.sql = ""
        self.params = None

    def execute(self, sql, params=None):
        self.sql = sql
        self.params = params

    def fetchone(self):
        if "GROUP BY business_category" in self.sql:
            return ("Food Processing", 1000, 70, 40, None, 76, None, 3)
        if "FROM location_reference" in self.sql:
            return ("Prayagraj", "Uttar Pradesh", "Prayagraj")
        return None

    def fetchall(self):
        if "business_reference_profiles" in self.sql:
            return [
                ("Bakery Products Unit", "Bakery", 80, 72, 35, 500),
                ("Bakery Products Unit", "Bakery", 78, 70, 36, 450),
                ("Spice Processing", "Spice Processing", 75, 69, 40, 300),
            ]
        if "ROW_NUMBER() OVER" in self.sql and "location_business_metrics" in self.sql:
            return [
                ("Food Processing", "Bakery", 70, 40, 76, 500, None, "2024-03-31"),
                ("Food Processing", "Spice Processing", 70, 40, 76, 500, None, "2024-03-31"),
            ]
        return []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class FakeConnection:
    def __init__(self):
        self.cursor_obj = FakeCursor()

    def cursor(self):
        return self.cursor_obj

    def close(self):
        pass


class TestBusinessInsights(unittest.TestCase):
    def test_category_aliases(self):
        self.assertEqual(canonical_category("Dairy"), "Agriculture Allied")
        self.assertEqual(canonical_category("Textiles"), "Manufacturing")
        self.assertEqual(canonical_category("Food Processing"), "Food Processing")

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

    def test_insights_aggregate_and_deduplicate(self):
        conn = FakeConnection()
        original_connect = InsightsService._connect
        original_ises = insights_service.ISESService

        class FakeISES:
            def __init__(self, *_args, **_kwargs):
                pass

            def get_for_location(self, *_args, **_kwargs):
                return {
                    "profit_business_pct": 60,
                    "bank_account_pct": 50,
                    "business_loan_pct": 30,
                    "competitor_monitoring_pct": 60,
                    "customer_feedback_pct": 70,
                    "monthly_budget_pct": 50,
                    "sales_target_pct": 60,
                    "electricity_use_pct": 90,
                    "power_outage_pct": 10,
                }

        try:
            InsightsService._connect = lambda self: conn
            insights_service.ISESService = FakeISES
            result = InsightsService("test").by_location("13", "Food Processing")
        finally:
            InsightsService._connect = original_connect
            insights_service.ISESService = original_ises

        self.assertTrue(result["available"])
        self.assertEqual(result["demand_score"], 70)
        self.assertEqual(result["competition_score"], 40)
        self.assertEqual(result["competition_count"], 1000)
        self.assertEqual(len(result["top_opportunities"]), 2)
        self.assertEqual(result["top_opportunities"][0]["business_name"], "Bakery Products Unit")
        self.assertEqual(result["opportunity_score"], 71.75)
        self.assertGreaterEqual(result["market_score"], 0)
        self.assertLessEqual(result["market_score"], 100)


if __name__ == "__main__":
    unittest.main()
