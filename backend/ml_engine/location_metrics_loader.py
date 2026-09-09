"""Loader for the agreed `location_business_metrics` database schema."""
from __future__ import annotations

import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv

load_dotenv()


class LocationMetricsLoader:
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL is missing from the environment")

    def get_metrics(
        self,
        location_id: str,
        category: str,
        subcategory: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        query = """
            SELECT metric_id, location_id, business_category, subcategory,
                   demand_score, competition_count, competition_score,
                   average_market_price, opportunity_score,
                   data_source, data_date, created_at, updated_at
            FROM location_business_metrics
            WHERE location_id = %s
              AND business_category = %s
              AND (%s IS NULL OR subcategory = %s OR subcategory IS NULL)
            ORDER BY data_date DESC NULLS LAST, updated_at DESC
            LIMIT 1
        """
        import psycopg2
        from psycopg2.extras import RealDictCursor
        with psycopg2.connect(self.database_url) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, (location_id, category, subcategory, subcategory))
                row = cursor.fetchone()
                return dict(row) if row else None
