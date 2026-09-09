from __future__ import annotations

import os
from typing import Any


class InsightsService:
    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or os.getenv("DATABASE_URL")

    def _connect(self):
        if not self.database_url:
            return None
        import psycopg2
        return psycopg2.connect(self.database_url)

    def locations(self) -> list[dict[str, Any]]:
        conn = self._connect()
        if conn is None:
            return []
        try:
            with conn.cursor() as cur:
                cur.execute("""SELECT location_id, location_name, state, district FROM location_reference ORDER BY state, district, location_name""")
                return [
                    {"location_id": str(r[0]), "location_name": r[1], "state": r[2], "district": r[3]}
                    for r in cur.fetchall()
                ]
        finally:
            conn.close()

    def by_location(self, location_id: str, category: str) -> dict[str, Any]:
        conn = self._connect()
        if conn is None:
            raise RuntimeError("DATABASE_URL is missing")
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT business_category,
                              AVG(demand_score), AVG(competition_score), AVG(competition_count),
                              AVG(average_market_price), AVG(opportunity_score),
                              MAX(data_date), COUNT(*)
                       FROM location_business_metrics
                       WHERE location_id = %s AND LOWER(business_category) = LOWER(%s)
                       GROUP BY business_category""",
                    (location_id, category),
                )
                row = cur.fetchone()
                if not row:
                    return {"available": False, "category": category, "message": "No location-specific market metrics are available for this category yet."}

                cur.execute(
                    """SELECT p.business_name, p.subcategory, m.opportunity_score, m.demand_score,
                              m.competition_score, m.competition_count
                       FROM location_business_metrics m
                       JOIN business_reference_profiles p
                         ON p.category = m.business_category
                        AND (p.subcategory = m.subcategory OR (p.subcategory IS NULL AND m.subcategory IS NULL))
                       WHERE m.location_id = %s AND LOWER(m.business_category) = LOWER(%s)
                       ORDER BY m.opportunity_score DESC NULLS LAST, m.demand_score DESC NULLS LAST
                       LIMIT 5""",
                    (location_id, category),
                )
                opportunities = [
                    {
                        "business_name": r[0], "subcategory": r[1],
                        "opportunity_score": float(r[2]) if r[2] is not None else None,
                        "demand_score": float(r[3]) if r[3] is not None else None,
                        "competition_score": float(r[4]) if r[4] is not None else None,
                        "competition_count": int(r[5]) if r[5] is not None else None,
                    }
                    for r in cur.fetchall()
                ]

                cur.execute("SELECT location_name, state, district FROM location_reference WHERE location_id = %s LIMIT 1", (location_id,))
                loc = cur.fetchone()
                return {
                    "available": True,
                    "location": {
                        "location_id": str(location_id),
                        "location_name": loc[0] if loc else None,
                        "state": loc[1] if loc else None,
                        "district": loc[2] if loc else None,
                    },
                    "category": category,
                    "demand_score": float(row[1]) if row[1] is not None else None,
                    "competition_score": float(row[2]) if row[2] is not None else None,
                    "competition_count": round(float(row[3])) if row[3] is not None else None,
                    "average_market_price": float(row[4]) if row[4] is not None else None,
                    "opportunity_score": float(row[5]) if row[5] is not None else None,
                    "data_date": row[6].isoformat() if row[6] else None,
                    "metric_rows": int(row[7]),
                    "top_opportunities": opportunities,
                    "source_note": "Location-specific database metrics; verify assumptions before investment.",
                }
        finally:
            conn.close()
