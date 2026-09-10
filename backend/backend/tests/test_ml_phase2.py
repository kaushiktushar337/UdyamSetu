import csv
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml_engine.profile_loader import BusinessProfile
from ml_engine.business_matcher import BusinessMatch
from ml_engine.recommendation_engine import RecommendationEngine, UserBusinessContext
from ml_engine.recommendation_pipeline import BusinessRecommendationPipeline
from ml_engine.decision_engine import BusinessAnalysisInput, calculate_business_analysis
from ml_engine.database_mapper import map_analysis_result
from ml_engine.database_contract import REFERENCE_PROFILE_COLUMNS, LOCATION_METRIC_COLUMNS, WRITE_TABLE_REQUIRED_COLUMNS
from ml_engine.feature_extractor import FeatureExtractor, FEATURE_NAMES
from ml_engine.calibration_model import ScoreCalibrator


def profile_from_csv():
    csv_path = ROOT / "seed_data" / "business_reference_profiles_database_ready.csv"
    with csv_path.open(encoding="utf-8", newline="") as f:
        row = next(csv.DictReader(f))
    numeric = {
        "minimum_capital", "typical_project_cost", "expected_monthly_revenue",
        "expected_monthly_expenses", "expected_profit_margin", "typical_break_even_months",
    }
    for key in numeric:
        row[key] = float(row[key]) if row.get(key) not in (None, "") else None
    return BusinessProfile(**{k: row[k] for k in BusinessProfile.__dataclass_fields__ if k in row})


class FakeMatcher:
    def __init__(self, matches): self.matches = matches
    def match(self, user_text, available_capital=None, top_k=5): return self.matches[:top_k]


class TestDatabaseContract(unittest.TestCase):
    def test_reference_csv_matches_contract(self):
        path = ROOT / "seed_data" / "business_reference_profiles_database_ready.csv"
        with path.open(encoding="utf-8", newline="") as f:
            header = set(next(csv.reader(f)))
        self.assertEqual(header, REFERENCE_PROFILE_COLUMNS)

    def test_sql_reference_contains_expected_schema_columns(self):
        sql = (ROOT / "database" / "ml_schema.sql").read_text(encoding="utf-8")
        for column in REFERENCE_PROFILE_COLUMNS - {"profile_id"}:
            self.assertIn(column, sql)
        for column in LOCATION_METRIC_COLUMNS - {"metric_id"}:
            self.assertIn(column, sql)


class TestRecommendationAndFeatures(unittest.TestCase):
    def setUp(self):
        self.profile = profile_from_csv()
        self.match = BusinessMatch(
            profile=self.profile,
            semantic_score=82.0,
            capital_score=88.0,
            final_score=83.5,
            reasons=["test"],
        )
        self.context = UserBusinessContext(
            available_capital=300000,
            interests="food processing bakery",
            skills="bakery food preparation business management",
            experience_years=2,
            available_resources=["supplier", "packaging"],
            infrastructure=["500 sq ft shed", "oven", "delivery vehicle"],
            location="India",
            location_id="00000000-0000-0000-0000-000000000001",
        )
        self.engine = RecommendationEngine()

    def test_generated_inputs_and_decision_engine(self):
        metrics = {
            "demand_score": 75,
            "competition_count": 12,
            "competition_score": 45,
            "average_market_price": 100,
            "opportunity_score": 70,
        }
        generated = self.engine.generate_inputs(self.context, self.match, metrics)
        analysis_input = BusinessAnalysisInput(
            financial=generated.financial,
            market=generated.market,
            operational=generated.operational,
            business_risks=generated.business_risks,
        )
        result = calculate_business_analysis(analysis_input)
        self.assertGreaterEqual(result.overall_score, 0)
        self.assertLessEqual(result.overall_score, 100)
        self.assertEqual(generated.market.demand_score, 75.0)
        self.assertEqual(generated.market.competition_score, 45.0)
        self.assertEqual(generated.market.opportunity_score, 70.0)
        self.assertEqual(generated.market.pricing_score, 50.0)

        features = FeatureExtractor().extract(self.context, self.match, generated, result)
        self.assertEqual(tuple(features.values.keys()), FEATURE_NAMES)
        self.assertEqual(len(features.ordered()), len(FEATURE_NAMES))
        self.assertTrue(all(isinstance(v, float) for v in features.ordered()))

        payload = map_analysis_result(result, analysis_input)
        for table, required in WRITE_TABLE_REQUIRED_COLUMNS.items():
            self.assertIn(table, payload)
            if isinstance(payload[table], dict):
                self.assertTrue(required.issubset(payload[table]))
        self.assertIsInstance(payload["business_analyses"]["confidence"], float)
        self.assertEqual(payload["financial_analyses"]["estimated_project_cost"], generated.financial.estimated_project_cost)

    def test_full_pipeline_with_fake_matcher(self):
        fake = FakeMatcher([self.match])
        pipeline = BusinessRecommendationPipeline([self.profile], matcher=fake)
        results = pipeline.recommend(self.context, top_k=1, location_metrics={
            "demand_score": 70,
            "competition_score": 40,
            "opportunity_score": 65,
        })
        self.assertEqual(len(results), 1)
        item = results[0]
        self.assertIn("features", item)
        self.assertIn("calibration", item)
        self.assertEqual(item["calibration"].score, item["analysis"].overall_score)
        self.assertFalse(item["calibration"].model_used)


class TestCalibration(unittest.TestCase):
    def test_training_and_prediction(self):
        profile = profile_from_csv()
        match = BusinessMatch(profile, 80, 80, 80, [])
        context = UserBusinessContext(available_capital=300000, interests="bakery", skills="bakery", experience_years=2)
        generated = RecommendationEngine().generate_inputs(context, match, {"demand_score": 70, "competition_score": 40, "opportunity_score": 65})
        result = calculate_business_analysis(BusinessAnalysisInput(generated.financial, generated.market, generated.operational, generated.business_risks))
        base = FeatureExtractor().extract(context, match, generated, result)

        # Create a deterministic labelled sample set only to verify model mechanics.
        samples = []
        targets = []
        for i in range(20):
            values = dict(base.values)
            values["semantic_match_score"] = 40 + i * 2
            values["market_score"] = 45 + i * 2
            values["risk_feasibility_score"] = 50 + i
            from ml_engine.feature_extractor import FeatureVector, FEATURE_SCHEMA_VERSION
            samples.append(FeatureVector(FEATURE_SCHEMA_VERSION, values))
            targets.append(min(100, 35 + i * 2.5))

        calibrator = ScoreCalibrator().fit(samples, targets)
        prediction = calibrator.predict(base, result.overall_score)
        self.assertTrue(prediction.model_used)
        self.assertGreaterEqual(prediction.score, 0)
        self.assertLessEqual(prediction.score, 100)


if __name__ == "__main__":
    unittest.main(verbosity=2)
