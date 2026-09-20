from __future__ import annotations

import os
from typing import Any

from ml_engine.ises_service import ISESService


# UI labels that existed in the prototype are normalized to the actual
# business-reference categories stored by UdyamSetu.
CATEGORY_ALIASES = {
    "dairy": "Agriculture Allied",
    "agriculture-linked activity": "Agriculture Allied",
    "agriculture allied": "Agriculture Allied",
    "food processing": "Food Processing",
    "manufacturing": "Manufacturing",
    "textiles": "Manufacturing",
    "rural manufacturing": "Rural Manufacturing",
    "services": "Services",
    "service": "Services",
    "retail": "Retail",
}


def canonical_category(category: str | None) -> str:
    value = (category or "").strip()
    return CATEGORY_ALIASES.get(value.lower(), value)


def clamp(value: Any, low: float = 0.0, high: float = 100.0) -> float:
    try:
        return max(low, min(high, float(value)))
    except (TypeError, ValueError):
        return 0.0


def weighted_average(values: list[tuple[Any, Any]]) -> float | None:
    """Weighted average using a positive business-count weight when available."""
    clean: list[tuple[float, float]] = []
    for value, weight in values:
        try:
            v = float(value)
        except (TypeError, ValueError):
            continue
        try:
            w = float(weight)
        except (TypeError, ValueError):
            w = 0.0
        if w <= 0:
            w = 1.0
        clean.append((v, w))
    if not clean:
        return None
    total_weight = sum(w for _, w in clean)
    return round(sum(v * w for v, w in clean) / total_weight, 2)


def local_environment_score(ises: dict[str, Any] | None) -> float | None:
    """Create one explainable 0-100 local-business-environment signal.

    This is deliberately a supporting signal, not a replacement for the
    location/category market score. Missing indicators are ignored and the
    remaining weights are renormalized.
    """
    if not ises:
        return None

    indicators = [
        ("profit_business_pct", 0.35, False),
        ("bank_account_pct", 0.15, False),
        ("business_loan_pct", 0.10, False),
        ("competitor_monitoring_pct", 0.10, False),
        ("customer_feedback_pct", 0.10, False),
        ("monthly_budget_pct", 0.05, False),
        ("sales_target_pct", 0.05, False),
        ("electricity_use_pct", 0.05, False),
        ("power_outage_pct", 0.05, True),
    ]

    total = 0.0
    weight_total = 0.0
    for name, weight, inverse in indicators:
        value = ises.get(name)
        if value is None:
            continue
        try:
            score = clamp(value)
        except (TypeError, ValueError):
            continue
        if inverse:
            score = 100.0 - score
        total += score * weight
        weight_total += weight

    if weight_total <= 0:
        return None
    return round(total / weight_total, 2)


def combine_opportunity(asuse_score: Any, environment_score: float | None) -> float | None:
    """Blend category opportunity with local business-environment context."""
    if asuse_score is None and environment_score is None:
        return None
    if asuse_score is None:
        return round(clamp(environment_score), 2)
    if environment_score is None:
        return round(clamp(asuse_score), 2)
    return round(
        0.75 * clamp(asuse_score) + 0.25 * clamp(environment_score),
        2,
    )


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
                cur.execute(
                    """
                    SELECT location_id, location_name, state, district
                    FROM location_reference
                    ORDER BY state, district, location_name
                    """
                )
                return [
                    {
                        "location_id": str(r[0]),
                        "location_name": r[1],
                        "state": r[2],
                        "district": r[3],
                    }
                    for r in cur.fetchall()
                ]
        finally:
            conn.close()

    def by_location(self, location_id: str, category: str) -> dict[str, Any]:
        requested_category = (category or "").strip()
        category = canonical_category(requested_category)
        conn = self._connect()
        if conn is None:
            raise RuntimeError("DATABASE_URL is missing")

        try:
            with conn.cursor() as cur:
                # First, get one row per subcategory, prioritizing the most reliable data source
                # This prevents double-counting when multiple data sources exist for the same subcategory
                cur.execute(
                    """
                    SELECT
                        business_category,
                        subcategory,
                        demand_score,
                        competition_score,
                        opportunity_score,
                        competition_count,
                        average_market_price,
                        data_date
                    FROM (
                        SELECT
                            business_category,
                            subcategory,
                            demand_score,
                            competition_score,
                            opportunity_score,
                            competition_count,
                            average_market_price,
                            data_date,
                            ROW_NUMBER() OVER (
                                PARTITION BY subcategory
                                ORDER BY
                                    CASE
                                        WHEN data_source = 'UdyamSetu synthetic prototype dataset' THEN 1
                                        WHEN data_source = 'ASUSE 2023-24 profile-aligned proxy' THEN 2
                                        WHEN data_source = 'ASUSE 2023-24 derived' THEN 3
                                        ELSE 4
                                    END
                            ) as rn
                        FROM location_business_metrics
                        WHERE location_id = %s
                          AND LOWER(business_category) = LOWER(%s)
                          AND COALESCE(data_source, '') <> 'UdyamSetu development seed'
                    ) ranked
                    WHERE rn = 1
                    """,
                    (location_id, category),
                )

                # Now compute weighted averages from the deduplicated subcategory data
                # One row per subcategory exists after deduplication.
                # Aggregate them using estimated business count instead of a
                # simple AVG, which prevents a small subcategory from having
                # the same influence as a large one.
                subcategory_rows = cur.fetchall()

                if not subcategory_rows:
                    # No data found for this location/category combination
                    return {
                        "location_id": str(location_id),
                        "location_name": None,
                        "state": None,
                        "district": None,
                        "category": requested_category or category,
                        "normalized_category": category,
                        "demand_score": None,
                        "competition_score": None,
                        "market_score": None,
                        "competition_count": 0,
                        "average_market_price": None,
                        "opportunity_score": None,
                        "market_opportunity_score": None,
                        "local_environment_score": None,
                        "data_date": None,
                        "metric_rows": 0,
                        "top_opportunities": [],
                    }

                # Compute weighted aggregates
                total_competition_count = sum(float(row[5]) for row in subcategory_rows if row[5] is not None)
                weighted_demand_sum = sum(
                    float(row[2]) * float(row[5]) if row[2] is not None and row[5] is not None else 0
                    for row in subcategory_rows
                )
                weighted_competition_sum = sum(
                    float(row[3]) * float(row[5]) if row[3] is not None and row[5] is not None else 0
                    for row in subcategory_rows
                )
                weighted_opportunity_sum = sum(
                    float(row[4]) * float(row[5]) if row[4] is not None and row[5] is not None else 0
                    for row in subcategory_rows
                )

                # For average market price, we only weight by subcategories that have price data
                price_rows = [row for row in subcategory_rows if row[6] is not None]
                total_price_weight = sum(float(row[5]) for row in price_rows if row[5] is not None)
                weighted_price_sum = sum(
                    float(row[6]) * float(row[5]) if row[6] is not None and row[5] is not None else 0
                    for row in price_rows
                )

                demand_score = (
                    weighted_demand_sum / total_competition_count
                    if total_competition_count > 0 else None
                )
                competition_score = (
                    weighted_competition_sum / total_competition_count
                    if total_competition_count > 0 else None
                )
                opportunity_score = (
                    weighted_opportunity_sum / total_competition_count
                    if total_competition_count > 0 else None
                )
                average_market_price = (
                    weighted_price_sum / total_price_weight
                    if total_price_weight > 0 else None
                )

                data_date = max((r[7] for r in subcategory_rows if r[7] is not None), default=None)

                if not subcategory_rows:
                    return {
                        "available": False,
                        "category": requested_category or category,
                        "normalized_category": category,
                        "message": "No location-specific market metrics are available for this category yet.",
                    }

                # The local environment is supporting context. It affects the
                # opportunity score, but never replaces demand or competition.
                cur.execute(
                    """
                    SELECT location_name, state, district
                    FROM location_reference
                    WHERE location_id = %s
                    LIMIT 1
                    """,
                    (location_id,),
                )
                loc = cur.fetchone()

                ises_context = None
                try:
                    ises_context = ISESService(self.database_url).get_for_location(
                        location_id,
                        category,
                    )
                except Exception:
                    # ISES is supplementary. A missing ISES row must never make
                    # the core location/category insights unavailable.
                    ises_context = None

                environment_score = local_environment_score(ises_context)

                # Retrieve all subcategory metrics first, then collapse duplicate
                # business names. The reference dataset contains some repeated
                # names across profiles; showing them twice is not useful to the user.
                # We use the same deduplication logic as above to avoid double-counting
                # due to multiple data sources per subcategory.
                cur.execute(
                    """
                    WITH deduplicated_metrics AS (
                        SELECT
                            business_category,
                            subcategory,
                            demand_score,
                            competition_score,
                            opportunity_score,
                            competition_count,
                            average_market_price,
                            data_date
                        FROM (
                            SELECT
                                business_category,
                                subcategory,
                                demand_score,
                                competition_score,
                                opportunity_score,
                                competition_count,
                                average_market_price,
                                data_date,
                                ROW_NUMBER() OVER (
                                    PARTITION BY subcategory
                                    ORDER BY
                                        CASE
                                            WHEN data_source = 'UdyamSetu synthetic prototype dataset' THEN 1
                                            WHEN data_source = 'ASUSE 2023-24 profile-aligned proxy' THEN 2
                                            WHEN data_source = 'ASUSE 2023-24 derived' THEN 3
                                            ELSE 4
                                        END
                                ) as rn
                            FROM location_business_metrics
                            WHERE location_id = %s
                              AND LOWER(business_category) = LOWER(%s)
                              AND COALESCE(data_source, '') <> 'UdyamSetu development seed'
                        ) ranked
                        WHERE rn = 1
                    )
                    SELECT
                        p.business_name,
                        p.subcategory,
                        m.opportunity_score,
                        m.demand_score,
                        m.competition_score,
                        m.competition_count
                    FROM deduplicated_metrics m
                    JOIN business_reference_profiles p
                      ON LOWER(p.category) = LOWER(m.business_category)
                     AND (
                          LOWER(COALESCE(p.subcategory, '')) = LOWER(COALESCE(m.subcategory, ''))
                          OR m.subcategory IS NULL
                          OR p.subcategory IS NULL
                     )
                    ORDER BY m.opportunity_score DESC NULLS LAST,
                             m.demand_score DESC NULLS LAST,
                             p.business_name
                    """,
                    (location_id, category),
                )

                unique: dict[str, dict[str, Any]] = {}
                for r in cur.fetchall():
                    name = str(r[0]).strip()
                    key = name.casefold()
                    if not name:
                        continue
                    combined = combine_opportunity(r[2], environment_score)
                    candidate = {
                        "business_name": name,
                        "subcategory": r[1],
                        "opportunity_score": combined,
                        "market_opportunity_score": clamp(r[2]) if r[2] is not None else None,
                        "demand_score": clamp(r[3]) if r[3] is not None else None,
                        "competition_score": clamp(r[4]) if r[4] is not None else None,
                        "competition_count": int(r[5]) if r[5] is not None else None,
                    }
                    previous = unique.get(key)
                    if previous is None or (
                        candidate["opportunity_score"] or 0
                    ) > (previous["opportunity_score"] or 0):
                        unique[key] = candidate

                opportunities = sorted(
                    unique.values(),
                    key=lambda item: (
                        item["opportunity_score"] is not None,
                        item["opportunity_score"] or 0,
                        item["demand_score"] or 0,
                    ),
                    reverse=True,
                )[:5]

                # These values come from the already-deduplicated and weighted
                # subcategory metrics above. The previous implementation still
                # referenced `row` from an older GROUP BY query that no longer
                # exists, which caused: NameError: name 'row' is not defined.
                asuse_opportunity = opportunity_score
                combined_category_opportunity = combine_opportunity(
                    asuse_opportunity,
                    environment_score,
                )
                demand_score = clamp(demand_score) if demand_score is not None else None
                competition_score = clamp(competition_score) if competition_score is not None else None
                market_score = None
                if demand_score is not None and competition_score is not None and combined_category_opportunity is not None:
                    # Competition is a pressure score, so its inverse is used.
                    market_score = round(
                        0.40 * demand_score
                        + 0.25 * (100.0 - competition_score)
                        + 0.35 * combined_category_opportunity,
                        2,
                    )

                return {
                    "available": True,
                    "location": {
                        "location_id": str(location_id),
                        "location_name": loc[0] if loc else None,
                        "state": loc[1] if loc else None,
                        "district": loc[2] if loc else None,
                    },
                    "category": requested_category or category,
                    "normalized_category": category,
                    "demand_score": demand_score,
                    "competition_score": competition_score,
                    "market_score": market_score,
                    "competition_count": int(round(total_competition_count)) if total_competition_count is not None else None,
                    # Only return a price when an actual metric row supplied it.
                    "average_market_price": float(average_market_price) if average_market_price is not None else None,
                    "opportunity_score": combined_category_opportunity,
                    "market_opportunity_score": clamp(asuse_opportunity) if asuse_opportunity is not None else None,
                    "local_environment_score": environment_score,
                    "data_date": data_date.isoformat() if hasattr(data_date, "isoformat") else (str(data_date) if data_date else None),
                    "metric_rows": len(subcategory_rows),
                    "top_opportunities": opportunities,
                }
        finally:
            conn.close()
