"""PostgreSQL persistence for the agreed UdyamSetu ML schema.

No tables or columns are invented here. The SQL targets only:
- business_analyses
- analysis_scores
- market_analyses
- operational_analyses
- financial_analyses
- analysis_risks
- analysis_recommendations
"""
from __future__ import annotations
import os
from typing import Any, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class AnalysisRepository:
    def __init__(self, database_url: Optional[str] = None, connection_factory=None):
        self.database_url = database_url or os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL is missing from the environment")
        self.connection_factory = connection_factory

    def _connect(self):
        if self.connection_factory is not None:
            return self.connection_factory(self.database_url)
        import psycopg2
        return psycopg2.connect(self.database_url)

    def save_analysis(
        self,
        *,
        user_id: str,
        business_id: str,
        location_id: str,
        payload: Dict[str, Any],
    ) -> str:
        """Persist one completed analysis and all child records atomically."""
        required_sections = {
            "business_analyses", "analysis_scores", "market_analyses",
            "operational_analyses", "financial_analyses",
            "analysis_risks", "analysis_recommendations",
        }
        missing = required_sections - set(payload)
        if missing:
            raise ValueError(f"Payload is missing sections: {sorted(missing)}")

        conn = self._connect()
        try:
            with conn.cursor() as cur:
                parent = payload["business_analyses"]
                cur.execute(
                    """
                    INSERT INTO business_analyses
                        (user_id, business_id, location_id, overall_score, decision,
                         confidence, analysis_status, engine_version)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING analysis_id
                    """,
                    (
                        user_id, business_id, location_id,
                        parent["overall_score"], parent["decision"], parent["confidence"],
                        parent.get("analysis_status", "completed"),
                        parent.get("engine_version", "decision-engine-v1"),
                    ),
                )
                analysis_id = str(cur.fetchone()[0])

                self._insert_one(cur, "analysis_scores", analysis_id, payload["analysis_scores"])
                self._insert_one(cur, "market_analyses", analysis_id, payload["market_analyses"])
                self._insert_one(cur, "operational_analyses", analysis_id, payload["operational_analyses"])
                self._insert_one(cur, "financial_analyses", analysis_id, payload["financial_analyses"])

                for risk in payload.get("analysis_risks", []):
                    cur.execute(
                        """
                        INSERT INTO analysis_risks
                            (analysis_id, risk_type, risk_score, severity, description, mitigation)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (analysis_id, risk.get("risk_type"), risk.get("risk_score"),
                         risk.get("severity"), risk.get("description"), risk.get("mitigation")),
                    )

                for rec in payload.get("analysis_recommendations", []):
                    cur.execute(
                        """
                        INSERT INTO analysis_recommendations
                            (analysis_id, category, priority, recommendation, expected_impact)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (analysis_id, rec.get("category"), rec.get("priority"),
                         rec["recommendation"], rec.get("expected_impact")),
                    )
            conn.commit()
            return analysis_id
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def _insert_one(cur, table: str, analysis_id: str, values: Dict[str, Any]) -> None:
        columns = ["analysis_id", *values.keys()]
        placeholders = ", ".join(["%s"] * len(columns))
        cur.execute(
            f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})",
            [analysis_id, *values.values()],
        )
