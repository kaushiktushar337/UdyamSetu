"""
Business profile loader for the UdyamSetu Decision Engine.

Reads the agreed `business_reference_profiles` table from PostgreSQL/Supabase
and converts rows into standardized BusinessProfile objects.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass
class BusinessProfile:
    profile_id: str
    business_name: str
    category: Optional[str] = None
    subcategory: Optional[str] = None
    minimum_capital: Optional[float] = None
    typical_project_cost: Optional[float] = None
    expected_monthly_revenue: Optional[float] = None
    expected_monthly_expenses: Optional[float] = None
    expected_profit_margin: Optional[float] = None
    typical_break_even_months: Optional[float] = None
    resource_requirements: Optional[str] = None
    infrastructure_requirements: Optional[str] = None
    risk_factors: Optional[str] = None
    data_source: Optional[str] = None

    def searchable_text(self) -> str:
        """Text representation used by the semantic business matcher."""
        parts = [
            self.business_name,
            self.category,
            self.subcategory,
            self.resource_requirements,
            self.infrastructure_requirements,
            self.risk_factors,
        ]
        return "\n".join(str(p) for p in parts if p)


class BusinessProfileLoader:
    """Loads business reference profiles from the project's PostgreSQL database."""

    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL is missing from the environment")

    def load_profiles(self, limit: Optional[int] = None) -> List[BusinessProfile]:
        query = """
            SELECT
                profile_id,
                business_name,
                category,
                subcategory,
                minimum_capital,
                typical_project_cost,
                expected_monthly_revenue,
                expected_monthly_expenses,
                expected_profit_margin,
                typical_break_even_months,
                resource_requirements,
                infrastructure_requirements,
                risk_factors,
                data_source
            FROM business_reference_profiles
            ORDER BY business_name
        """
        if limit is not None:
            query += " LIMIT %s"

        import psycopg2
        conn = psycopg2.connect(self.database_url)
        cursor = conn.cursor()

        try:
            cursor.execute(query, (limit,) if limit is not None else None)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return [BusinessProfile(**dict(zip(columns, row))) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def get_profile(self, profile_id: str) -> Optional[BusinessProfile]:
        import psycopg2
        conn = psycopg2.connect(self.database_url)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT
                    profile_id, business_name, category, subcategory,
                    minimum_capital, typical_project_cost,
                    expected_monthly_revenue, expected_monthly_expenses,
                    expected_profit_margin, typical_break_even_months,
                    resource_requirements, infrastructure_requirements,
                    risk_factors, data_source
                FROM business_reference_profiles
                WHERE profile_id = %s
            """, (profile_id,))
            row = cursor.fetchone()
            if not row:
                return None
            columns = [desc[0] for desc in cursor.description]
            return BusinessProfile(**dict(zip(columns, row)))
        finally:
            cursor.close()
            conn.close()


def load_business_profiles(database_url: Optional[str] = None) -> List[BusinessProfile]:
    """Convenience function for loading all profiles."""
    return BusinessProfileLoader(database_url).load_profiles()
