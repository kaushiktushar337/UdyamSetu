from __future__ import annotations

import os
import logging
from typing import Any, Iterable

from ml_engine.ises_service import ISESService


logger = logging.getLogger(__name__)


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


def normalize_score(value: Any) -> float | None:
    """Return a stored 0-100 score without hiding malformed data."""
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not 0 <= number <= 100:
        return None
    return round(number, 2)


def clamp(value: Any, low: float = 0.0, high: float = 100.0) -> float:
    """Compatibility helper for callers outside this service."""
    normalized = normalize_score(value)
    if normalized is None:
        return 0.0
    return max(low, min(high, normalized))


def local_environment_score(ises: dict[str, Any] | None) -> float | None:
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
        value = normalize_score(ises.get(name))
        if value is None:
            continue
        if inverse:
            value = 100.0 - value
        total += value * weight
        weight_total += weight
    return round(total / weight_total, 2) if weight_total else None


def combine_opportunity(market_score: Any, environment_score: float | None) -> float | None:
    market = normalize_score(market_score)
    environment = normalize_score(environment_score)
    if market is None and environment is None:
        return None
    if market is None:
        return environment
    if environment is None:
        return market
    return round(0.75 * market + 0.25 * environment, 2)


def _is_verified_local_count_source(data_source: Any) -> bool:
    """Whether a metric source is explicitly safe for a local business count.

    ASUSE-derived/proxy rows in the current database are survey/population
    metrics that have been copied into location_business_metrics but are not
    proven to be Prayagraj/category-local counts. Summing them creates the
    21,066,374 inflation. The synthetic prototype rows, however, are explicitly
    generated per selected location and business profile to provide the
    location-aware development market estimate, so they may be used as the
    application's synthetic estimated-business metric (clearly labeled as such).
    """
    source = str(data_source or "").strip().casefold()
    return (
        "verified local" in source
        or "location-specific" in source
        or "synthetic prototype" in source
    )


def aggregate_metric_rows(rows: Iterable[dict[str, Any]], fallback_competition_count: int | float | None = None) -> dict[str, Any]:
    """Aggregate one authoritative row per subcategory without fabricating counts.

    Competition count is *not* summed unless the source explicitly identifies
    the value as a verified location-specific count. When no such market-count
    row exists, an explicitly supplied local sector estimate (for example, the
    ISES city-sector weighted_businesses value) may be used as a fallback.
    """
    rows = list(rows)
    local_count_rows = [
        r for r in rows
        if r.get("competition_count") is not None
        and _is_verified_local_count_source(r.get("data_source"))
    ]
    count = (
        sum(int(r["competition_count"]) for r in local_count_rows)
        if local_count_rows
        else None
    )
    weighted = [r for r in rows if r.get("competition_count") not in (None, 0)]

    def wavg(field: str) -> float | None:
        if not weighted:
            return None
        values = [
            (normalize_score(r.get(field)) if field != "average_market_price" else _number(r.get(field)), int(r["competition_count"]))
            for r in weighted
        ]
        values = [(v, w) for v, w in values if v is not None]
        if not values:
            return None
        total = sum(w for _, w in values)
        return round(sum(v * w for v, w in values) / total, 2) if total else None

    price_rows = [
        (r.get("average_market_price"), int(r["competition_count"]))
        for r in rows
        if r.get("average_market_price") is not None and r.get("competition_count") not in (None, 0)
    ]
    price = None
    if price_rows:
        price = round(sum(float(v) * w for v, w in price_rows) / sum(w for _, w in price_rows), 2)

    if count is None and fallback_competition_count is not None:
        try:
            fallback = float(fallback_competition_count)
            count = int(round(fallback)) if fallback >= 0 else None
        except (TypeError, ValueError):
            count = None

    return {
        "competition_count": count if rows else None,
        "demand_score": wavg("demand_score"),
        "competition_score": wavg("competition_score"),
        "market_opportunity_score": wavg("opportunity_score"),
        "average_market_price": price,
        "data_date": max((r.get("data_date") for r in rows if r.get("data_date")), default=None),
        "metric_rows": len(rows),
    }


def _number(value: Any) -> float | None:
    try:
        return None if value is None else float(value)
    except (TypeError, ValueError):
        return None


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

    def _resolve_category_filter(self, cur, requested: str) -> tuple[str, str | None]:
        """Resolve a top-level category or an exact reference subcategory."""
        normalized = canonical_category(requested)
        cur.execute(
            """
            SELECT MIN(category) AS business_category
            FROM business_reference_profiles
            WHERE LOWER(TRIM(category)) = LOWER(TRIM(%s))
            """,
            (normalized,),
        )
        row = cur.fetchone()
        if row and row[0]:
            return str(row[0]), None

        cur.execute(
            """
            SELECT MIN(category) AS business_category
            FROM business_reference_profiles
            WHERE LOWER(TRIM(subcategory)) = LOWER(TRIM(%s))
            """,
            (normalized,),
        )
        row = cur.fetchone()
        if row and row[0]:
            return str(row[0]), normalized
        return normalized, None

    def _metric_rows(self, cur, location_id: str, category: str, subcategory: str | None = None) -> list[dict[str, Any]]:
        """Select exactly one authoritative metric row per subcategory.

        Priority is explicit: location-specific synthetic market data first for
        the development Business Insights experience, then ASUSE-derived data
        and profile-aligned ASUSE proxy rows only for subcategories that do
        not have a synthetic local metric. Development seed rows are excluded.
        """
        cur.execute(
            """
            WITH ranked AS (
                SELECT
                    lbm.*,
                    ROW_NUMBER() OVER (
                        PARTITION BY
                            lbm.location_id,
                            LOWER(lbm.business_category),
                            LOWER(COALESCE(lbm.subcategory, ''))
                        ORDER BY
                            CASE
                                WHEN LOWER(COALESCE(lbm.data_source, '')) LIKE '%%synthetic%%' THEN 1
                                WHEN LOWER(COALESCE(lbm.data_source, '')) LIKE '%%asuse%%derived%%' THEN 2
                                WHEN LOWER(COALESCE(lbm.data_source, '')) LIKE '%%asuse%%proxy%%' THEN 3
                                ELSE 4
                            END,
                            lbm.data_date DESC NULLS LAST,
                            lbm.updated_at DESC NULLS LAST,
                            lbm.created_at DESC NULLS LAST
                    ) AS rn
                FROM location_business_metrics lbm
                WHERE lbm.location_id = %s
                  AND LOWER(lbm.business_category) = LOWER(%s)
                  AND (%s IS NULL OR LOWER(COALESCE(lbm.subcategory, '')) = LOWER(%s))
                  AND LOWER(COALESCE(lbm.data_source, '')) <> 'udyamsetu development seed'
            )
            SELECT
                business_category,
                subcategory,
                demand_score,
                competition_score,
                opportunity_score,
                competition_count,
                average_market_price,
                data_date,
                data_source
            FROM ranked
            WHERE rn = 1
            ORDER BY subcategory
            """,
            (location_id, category, subcategory, subcategory),
        )
        rows = cur.fetchall()
        logger.info(
            "Business Insights metric selection: location_id=%s category=%s subcategory=%s rows=%s",
            location_id, category, subcategory, len(rows),
        )
        return [
            {
                "business_category": r[0],
                "subcategory": r[1],
                "demand_score": r[2],
                "competition_score": r[3],
                "opportunity_score": r[4],
                "competition_count": r[5],
                "average_market_price": r[6],
                "data_date": r[7].isoformat() if r[7] else None,
                "data_source": r[8],
            }
            for r in rows
        ]

    def by_location(self, location_id: str, category: str) -> dict[str, Any]:
        requested_category = (category or "").strip()
        normalized_category = canonical_category(requested_category)
        conn = self._connect()
        if conn is None:
            raise RuntimeError("DATABASE_URL is missing")

        try:
            with conn.cursor() as cur:
                resolved_category, resolved_subcategory = self._resolve_category_filter(
                    cur, normalized_category
                )
                metric_rows = self._metric_rows(
                    cur, location_id, resolved_category, resolved_subcategory
                )
                if not metric_rows:
                    return {
                        "available": False,
                        "location_id": str(location_id),
                        "category": requested_category or normalized_category,
                        "normalized_category": normalized_category,
                        "demand_score": None,
                        "competition_score": None,
                        "market_score": None,
                        "competition_count": None,
                        "average_market_price": None,
                        "opportunity_score": None,
                        "market_opportunity_score": None,
                        "local_environment_score": None,
                        "data_date": None,
                        "metric_rows": 0,
                        "top_opportunities": [],
                    }

                normalized_category = resolved_category
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

                try:
                    ises_context = ISESService(self.database_url).get_for_location(
                        location_id, normalized_category
                    )
                except Exception:
                    logger.exception(
                        "ISES lookup failed: location_id=%s category=%s",
                        location_id, normalized_category,
                    )
                    ises_context = None

                ises_business_count = None
                if ises_context and ises_context.get("weighted_businesses") is not None:
                    try:
                        ises_business_count = float(ises_context["weighted_businesses"])
                    except (TypeError, ValueError):
                        ises_business_count = None

                aggregate = aggregate_metric_rows(
                    metric_rows,
                    fallback_competition_count=ises_business_count,
                )
                competition_count_source = (
                    "verified local market metric"
                    if any(_is_verified_local_count_source(r.get("data_source")) for r in metric_rows)
                    else ("ISES city-sector weighted business estimate" if ises_business_count is not None else None)
                )
                logger.info(
                    "Business Insights aggregate: location_id=%s category=%s metric_rows=%s competition_count=%s source=%s demand=%s competition=%s market_opportunity=%s price=%s",
                    location_id, normalized_category, aggregate["metric_rows"],
                    aggregate["competition_count"], competition_count_source, aggregate["demand_score"],
                    aggregate["competition_score"], aggregate["market_opportunity_score"],
                    aggregate["average_market_price"],
                )

                environment_score = local_environment_score(ises_context)
                market_opportunity = aggregate["market_opportunity_score"]
                combined_opportunity = combine_opportunity(market_opportunity, environment_score)

                market_score = None
                demand_score = aggregate["demand_score"]
                competition_score = aggregate["competition_score"]
                if demand_score is not None and competition_score is not None and combined_opportunity is not None:
                    market_score = round(
                        0.40 * demand_score
                        + 0.25 * (100.0 - competition_score)
                        + 0.35 * combined_opportunity,
                        2,
                    )

                # Exact category/subcategory matching prevents a category-wide
                # metric from multiplying against every profile in the category.
                cur.execute(
                    """
                    WITH unique_profiles AS (
                        SELECT
                            LOWER(TRIM(category)) AS category_key,
                            LOWER(TRIM(COALESCE(subcategory, ''))) AS subcategory_key,
                            MIN(business_name) AS business_name,
                            MIN(subcategory) AS subcategory
                        FROM business_reference_profiles
                        WHERE LOWER(TRIM(category)) = LOWER(TRIM(%s))
                          AND (%s IS NULL OR LOWER(TRIM(COALESCE(subcategory, ''))) = LOWER(TRIM(%s)))
                        GROUP BY 1,2
                    )
                    SELECT
                        p.business_name,
                        p.subcategory,
                        m.opportunity_score,
                        m.demand_score,
                        m.competition_score,
                        m.competition_count,
                        m.data_source
                    FROM unique_profiles p
                    JOIN (
                        SELECT *
                        FROM (
                            SELECT
                                lbm.*,
                                ROW_NUMBER() OVER (
                                    PARTITION BY LOWER(COALESCE(lbm.subcategory, ''))
                                    ORDER BY
                                        CASE
                                            WHEN LOWER(COALESCE(lbm.data_source, '')) LIKE '%%asuse%%derived%%' THEN 1
                                            WHEN LOWER(COALESCE(lbm.data_source, '')) LIKE '%%asuse%%proxy%%' THEN 2
                                            WHEN LOWER(COALESCE(lbm.data_source, '')) LIKE '%%synthetic%%' THEN 3
                                            ELSE 4
                                        END,
                                        lbm.data_date DESC NULLS LAST,
                                        lbm.updated_at DESC NULLS LAST,
                                        lbm.created_at DESC NULLS LAST
                                ) AS rn
                            FROM location_business_metrics lbm
                            WHERE lbm.location_id = %s
                              AND LOWER(lbm.business_category) = LOWER(%s)
                              AND lbm.subcategory IS NOT NULL
                              AND (%s IS NULL OR LOWER(TRIM(lbm.subcategory)) = LOWER(TRIM(%s)))
                              AND LOWER(COALESCE(lbm.data_source, '')) <> 'udyamsetu development seed'
                        ) ranked
                        WHERE rn = 1
                    ) m
                      ON LOWER(TRIM(COALESCE(m.subcategory, ''))) = p.subcategory_key
                    ORDER BY m.opportunity_score DESC NULLS LAST,
                             m.demand_score DESC NULLS LAST,
                             p.business_name
                    """,
                    (normalized_category, resolved_subcategory, resolved_subcategory, location_id, normalized_category, resolved_subcategory, resolved_subcategory),
                )

                opportunities = []
                seen_names: set[str] = set()
                for r in cur.fetchall():
                    name = str(r[0]).strip()
                    key = name.casefold()
                    if not name or key in seen_names:
                        continue
                    seen_names.add(key)
                    opportunities.append(
                        {
                            "business_name": name,
                            "subcategory": r[1],
                            "opportunity_score": combine_opportunity(r[2], environment_score),
                            "market_opportunity_score": normalize_score(r[2]),
                            "demand_score": normalize_score(r[3]),
                            "competition_score": normalize_score(r[4]),
                            "competition_count": (
                                int(r[5])
                                if r[5] is not None and _is_verified_local_count_source(r[6])
                                else (
                                    int(round(ises_business_count))
                                    if ises_business_count is not None else None
                                )
                            ),
                        }
                    )
                opportunities = opportunities[:5]

                return {
                    "available": True,
                    "location": {
                        "location_id": str(location_id),
                        "location_name": loc[0] if loc else None,
                        "state": loc[1] if loc else None,
                        "district": loc[2] if loc else None,
                    },
                    "category": requested_category or normalized_category,
                    "normalized_category": normalized_category,
                    "demand_score": demand_score,
                    "competition_score": competition_score,
                    "market_score": market_score,
                    "competition_count": aggregate["competition_count"],
                    "competition_count_source": competition_count_source,
                    "average_market_price": aggregate["average_market_price"],
                    "opportunity_score": combined_opportunity,
                    "market_opportunity_score": market_opportunity,
                    "local_environment_score": environment_score,
                    "data_date": aggregate["data_date"],
                    "metric_rows": aggregate["metric_rows"],
                    "top_opportunities": opportunities,
                }
        finally:
            conn.close()
