import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml_engine.profile_loader import BusinessProfileLoader, BusinessProfile
from ml_engine.business_matcher import BusinessMatch
from ml_engine.recommendation_engine import RecommendationEngine, UserBusinessContext
from ml_engine.decision_engine import BusinessAnalysisInput, calculate_business_analysis
from ml_engine.database_mapper import map_analysis_result
from ml_engine.confidence import estimate_confidence
from ml_engine.analysis_repository import AnalysisRepository


class FakeCursor:
    def __init__(self): self.calls = []; self.analysis_id = "11111111-1111-1111-1111-111111111111"
    def execute(self, sql, params=None): self.calls.append((" ".join(sql.split()), params))
    def fetchone(self): return [self.analysis_id]
    def __enter__(self): return self
    def __exit__(self, *args): return False

class FakeConnection:
    def __init__(self): self.cursor_obj = FakeCursor(); self.committed=False; self.rolled=False; self.closed=False
    def cursor(self): return self.cursor_obj
    def commit(self): self.committed=True
    def rollback(self): self.rolled=True
    def close(self): self.closed=True


def make_result():
    profiles = BusinessProfileLoader.load_profiles_from_csv(str(ROOT / "seed_data" / "business_reference_profiles_database_ready.csv"))
    profile = profiles[0]
    match = BusinessMatch(profile, 82, 88, 83.5, ["test"])
    context = UserBusinessContext(available_capital=300000, interests="food bakery", skills="bakery supplier", experience_years=2)
    generated = RecommendationEngine().generate_inputs(context, match, {
        "demand_score": 75, "competition_score": 45, "opportunity_score": 70
    })
    analysis_input = BusinessAnalysisInput(generated.financial, generated.market, generated.operational, generated.business_risks)
    analysis = calculate_business_analysis(analysis_input)
    return profile, generated, analysis, analysis_input


class TestCompleteDecisionEngine(unittest.TestCase):
    def test_offline_csv_loader_loads_database_ready_profiles(self):
        profiles = BusinessProfileLoader.load_profiles_from_csv(str(ROOT / "seed_data" / "business_reference_profiles_database_ready.csv"))
        self.assertGreaterEqual(len(profiles), 40)
        self.assertTrue(all(p.profile_id and p.business_name for p in profiles))

    def test_confidence_is_numeric_and_bounded(self):
        profile, generated, analysis, analysis_input = make_result()
        confidence = estimate_confidence(profile, generated)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
        payload = map_analysis_result(analysis, analysis_input, confidence=confidence)
        self.assertEqual(payload["business_analyses"]["confidence"], confidence)

    def test_payload_matches_all_write_tables(self):
        _, _, analysis, analysis_input = make_result()
        payload = map_analysis_result(analysis, analysis_input, confidence=0.8123, engine_version="decision-engine-v1")
        self.assertEqual(payload["business_analyses"]["engine_version"], "decision-engine-v1")
        self.assertEqual(payload["business_analyses"]["confidence"], 0.8123)
        self.assertEqual(payload["financial_analyses"]["available_capital"], analysis_input.financial.available_capital + analysis_input.financial.funding_available)

    def test_repository_uses_agreed_table_names_and_atomic_write(self):
        _, _, analysis, analysis_input = make_result()
        payload = map_analysis_result(analysis, analysis_input, confidence=0.8)
        fake_conn = FakeConnection()
        repo = AnalysisRepository("postgresql://test", connection_factory=lambda _: fake_conn)
        analysis_id = repo.save_analysis(
            user_id="u", business_id="b", location_id="l", payload=payload
        )
        self.assertEqual(analysis_id, fake_conn.cursor_obj.analysis_id)
        self.assertTrue(fake_conn.committed)
        sql = "\n".join(call[0] for call in fake_conn.cursor_obj.calls)
        for table in ["business_analyses", "analysis_scores", "market_analyses", "operational_analyses", "financial_analyses", "analysis_risks", "analysis_recommendations"]:
            self.assertIn(table, sql)

if __name__ == "__main__":
    unittest.main(verbosity=2)

class TestSchemaAndServiceIntegration(unittest.TestCase):
    def test_reference_schema_contains_exact_persistence_contract(self):
        sql = (ROOT / "database_schema_reference.sql").read_text(encoding="utf-8")
        expected = {
            "business_analyses": ["user_id", "business_id", "location_id", "overall_score", "decision", "confidence", "analysis_status", "engine_version"],
            "analysis_scores": ["analysis_id", "market_score", "operational_score", "financial_score", "risk_score", "overall_score"],
            "market_analyses": ["analysis_id", "demand_score", "competition_score", "market_gap_score", "pricing_score", "opportunity_score"],
            "operational_analyses": ["analysis_id", "resource_score", "infrastructure_score", "supply_chain_score", "logistics_score", "operational_score"],
            "financial_analyses": ["analysis_id", "estimated_project_cost", "available_capital", "funding_gap", "estimated_monthly_revenue", "estimated_monthly_expenses", "estimated_monthly_profit", "break_even_months"],
            "analysis_risks": ["analysis_id", "risk_type", "risk_score", "severity", "description", "mitigation"],
            "analysis_recommendations": ["analysis_id", "category", "priority", "recommendation", "expected_impact"],
        }
        for table, columns in expected.items():
            self.assertIn(f"CREATE TABLE IF NOT EXISTS {table}", sql)
            for column in columns:
                self.assertIn(column, sql)

    def test_repository_rolls_back_on_write_error(self):
        class FailingCursor(FakeCursor):
            def execute(self, sql, params=None):
                super().execute(sql, params)
                if "analysis_scores" in sql:
                    raise RuntimeError("simulated write failure")
        class FailingConnection(FakeConnection):
            def __init__(self):
                super().__init__(); self.cursor_obj = FailingCursor()
        _, _, analysis, analysis_input = make_result()
        payload = map_analysis_result(analysis, analysis_input, confidence=0.8)
        conn = FailingConnection()
        repo = AnalysisRepository("postgresql://test", connection_factory=lambda _: conn)
        with self.assertRaises(RuntimeError):
            repo.save_analysis(user_id="u", business_id="b", location_id="l", payload=payload)
        self.assertTrue(conn.rolled)
        self.assertFalse(conn.committed)

    def test_service_adds_numeric_confidence_to_recommendations(self):
        from ml_engine.recommendation_pipeline import BusinessRecommendationPipeline
        from ml_engine.decision_service import UdyamSetuDecisionService
        profile, _, _, _ = make_result()
        match = BusinessMatch(profile, 82, 88, 83.5, ["test"])
        class OneMatcher:
            def match(self, *args, **kwargs): return [match]
        pipeline = BusinessRecommendationPipeline([profile], matcher=OneMatcher())
        service = UdyamSetuDecisionService(pipeline)
        results = service.recommend(
            UserBusinessContext(available_capital=300000, interests="food bakery", skills="bakery", experience_years=2),
            top_k=1,
        )
        self.assertEqual(len(results), 1)
        self.assertGreaterEqual(results[0]["confidence"], 0.0)
        self.assertLessEqual(results[0]["confidence"], 1.0)
