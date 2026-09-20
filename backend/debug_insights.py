#!/usr/bin/env python
"""Trace the complete Business Insights data path against the configured DB."""
import os
import pprint

import psycopg2

from api.insights_service import InsightsService, canonical_category


def main():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    conn = psycopg2.connect(database_url)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT location_id, location_name, state, district
        FROM location_reference
        WHERE LOWER(location_name) = 'prayagraj'
           OR LOWER(district) = 'prayagraj'
        ORDER BY CASE WHEN LOWER(location_name) = 'prayagraj' THEN 0 ELSE 1 END
        LIMIT 1
        """
    )
    location = cur.fetchone()
    if not location:
        raise RuntimeError("Prayagraj is not present in location_reference")

    location_id = str(location[0])
    category = "Food Processing"

    print("=" * 80)
    print("BUSINESS INSIGHTS ROOT-CAUSE TRACE")
    print("=" * 80)
    print("Location:", location)
    print("Requested category:", category)
    print("Normalized category:", canonical_category(category))

    print("\n1. Raw location_business_metrics rows")
    cur.execute(
        """
        SELECT business_category, subcategory, demand_score,
               competition_score, opportunity_score, competition_count,
               average_market_price, data_date, data_source
        FROM location_business_metrics
        WHERE location_id = %s
          AND LOWER(business_category) = LOWER(%s)
        ORDER BY subcategory, data_date DESC, data_source
        """,
        (location_id, canonical_category(category)),
    )
    raw = cur.fetchall()
    for row in raw:
        print(row)
    print("Raw row count:", len(raw))

    print("\n2. Duplicate natural keys")
    cur.execute(
        """
        SELECT location_id, business_category, subcategory, data_date,
               COALESCE(data_source, ''), COUNT(*)
        FROM location_business_metrics
        WHERE location_id = %s
          AND LOWER(business_category) = LOWER(%s)
        GROUP BY location_id, business_category, subcategory, data_date,
                 COALESCE(data_source, '')
        HAVING COUNT(*) > 1
        """,
        (location_id, canonical_category(category)),
    )
    print(cur.fetchall())

    print("\n3. Duplicate logical business profiles")
    cur.execute(
        """
        SELECT business_name, category, subcategory, COUNT(*)
        FROM business_reference_profiles
        GROUP BY business_name, category, subcategory
        HAVING COUNT(*) > 1
        """
    )
    print(cur.fetchall())

    print("\n4. Profile join cardinality by subcategory")
    cur.execute(
        """
        SELECT m.subcategory, m.competition_count, COUNT(p.profile_id)
        FROM location_business_metrics m
        LEFT JOIN business_reference_profiles p
          ON LOWER(TRIM(p.category)) = LOWER(TRIM(m.business_category))
         AND LOWER(TRIM(COALESCE(p.subcategory, ''))) =
             LOWER(TRIM(COALESCE(m.subcategory, '')))
        WHERE m.location_id = %s
          AND LOWER(m.business_category) = LOWER(%s)
        GROUP BY m.subcategory, m.competition_count
        ORDER BY m.subcategory
        """,
        (location_id, canonical_category(category)),
    )
    for row in cur.fetchall():
        print(row)

    print("\n5. ISES rows for this location/category")
    cur.execute(
        """
        SELECT city, sector, weighted_businesses, data_source, data_date
        FROM ises_city_sector_metrics
        WHERE location_id = %s
        ORDER BY data_date DESC
        """,
        (location_id,),
    )
    for row in cur.fetchall():
        print(row)

    conn.close()

    print("\n6. Exact InsightsService response")
    result = InsightsService(database_url).by_location(location_id, category)
    pprint.pp(result, sort_dicts=False)

    print("\n7. Competition-count regression")
    print("Returned:", result.get("competition_count"))
    print("Bad historical value:", 21066374)
    print("PASS" if result.get("competition_count") != 21066374 else "FAIL")


if __name__ == "__main__":
    main()
