#!/usr/bin/env python
"""Debug script to trace Business Insights data flow."""
import psycopg2
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres.pocxoncclomzbyaoldqn:udyamsetu2026@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"
)

def main():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # 1. Get Prayagraj location
    print("=" * 60)
    print("1. LOCATION REFERENCE for Prayagraj")
    print("=" * 60)
    cur.execute("""
        SELECT location_id, location_name, state, district
        FROM location_reference
        WHERE LOWER(district) = 'prayagraj'
        ORDER BY location_name
    """)
    locations = cur.fetchall()
    for row in locations:
        print(f"  {row}")

    if not locations:
        print("  NO LOCATIONS FOUND")
        conn.close()
        return

    location_id = locations[0][0]
    print(f"\n  Using location_id: {location_id}")

    # 2. Get location_business_metrics for Food Processing
    print("\n" + "=" * 60)
    print("2. LOCATION BUSINESS METRICS (Food Processing)")
    print("=" * 60)
    cur.execute("""
        SELECT
            business_category,
            subcategory,
            competition_count,
            demand_score,
            competition_score,
            opportunity_score,
            average_market_price,
            data_date,
            data_source
        FROM location_business_metrics
        WHERE location_id = %s
          AND LOWER(business_category) = 'food processing'
        ORDER BY subcategory, data_date DESC
    """, (str(location_id),))

    metrics = cur.fetchall()
    print(f"  Found {len(metrics)} rows:")
    total_competition = 0
    for row in metrics:
        print(f"    {row}")
        if row[2]:  # competition_count
            total_competition += row[2]
    print(f"\n  SUM of competition_count: {total_competition}")

    # 3. Check for duplicate natural keys in location_business_metrics
    print("\n" + "=" * 60)
    print("3. CHECK DUPLICATE NATURAL KEYS in location_business_metrics")
    print("=" * 60)
    cur.execute("""
        SELECT location_id, business_category, subcategory, data_date, data_source, COUNT(*) as cnt
        FROM location_business_metrics
        WHERE location_id = %s
          AND LOWER(business_category) = 'food processing'
        GROUP BY location_id, business_category, subcategory, data_date, data_source
        HAVING COUNT(*) > 1
    """, (str(location_id),))

    duplicates = cur.fetchall()
    if duplicates:
        print(f"  Found {len(duplicates)} duplicate groups:")
        for row in duplicates:
            print(f"    {row}")
    else:
        print("  No duplicate natural keys found")

    # 4. Check business_reference_profiles for duplicates
    print("\n" + "=" * 60)
    print("4. BUSINESS REFERENCE PROFILES (Food Processing)")
    print("=" * 60)
    cur.execute("""
        SELECT business_name, category, subcategory, COUNT(*) as cnt
        FROM business_reference_profiles
        WHERE LOWER(category) = 'food processing'
        GROUP BY business_name, category, subcategory
        HAVING COUNT(*) > 1
    """)

    profile_dups = cur.fetchall()
    if profile_dups:
        print(f"  Found {len(profile_dups)} duplicate profiles:")
        for row in profile_dups:
            print(f"    {row}")
    else:
        print("  No duplicate profiles found")

    # 5. Get all profiles for Food Processing
    cur.execute("""
        SELECT DISTINCT business_name, category, subcategory
        FROM business_reference_profiles
        WHERE LOWER(category) = 'food processing'
        ORDER BY business_name
    """)

    profiles = cur.fetchall()
    print(f"  Total unique Food Processing profiles: {len(profiles)}")
    for p in profiles[:10]:
        print(f"    {p}")
    if len(profiles) > 10:
        print(f"    ... and {len(profiles) - 10} more")

    # 6. Check the actual join that InsightsService does
    print("\n" + "=" * 60)
    print("6. TEST JOIN: location_business_metrics + business_reference_profiles")
    print("=" * 60)
    cur.execute("""
        SELECT
            m.business_category,
            m.subcategory,
            m.competition_count,
            p.business_name,
            p.subcategory as profile_subcategory
        FROM location_business_metrics m
        JOIN business_reference_profiles p
          ON LOWER(p.category) = LOWER(m.business_category)
         AND (
              LOWER(COALESCE(p.subcategory, '')) = LOWER(COALESCE(m.subcategory, ''))
              OR m.subcategory IS NULL
              OR p.subcategory IS NULL
         )
        WHERE m.location_id = %s
          AND LOWER(m.business_category) = 'food processing'
        ORDER BY m.opportunity_score DESC NULLS LAST
        LIMIT 15
    """, (str(location_id),))

    join_results = cur.fetchall()
    print(f"  Join returns {len(join_results)} rows:")
    for row in join_results:
        print(f"    {row}")

    # 7. Check ISES data
    print("\n" + "=" * 60)
    print("7. ISES DATA for Prayagraj")
    print("=" * 60)
    cur.execute("""
        SELECT city, sector, weighted_businesses, profit_business_pct,
               bank_account_pct, business_loan_pct, data_date
        FROM ises_city_sector_metrics
        WHERE LOWER(city) LIKE '%prayagraj%'
           OR city = (SELECT location_name FROM location_reference WHERE location_id = %s)
        LIMIT 10
    """, (str(location_id),))

    ises_data = cur.fetchall()
    if ises_data:
        print(f"  Found {len(ises_data)} ISES rows:")
        for row in ises_data:
            print(f"    {row}")
    else:
        print("  No ISES data found for Prayagraj")

    # 8. Run the actual InsightsService query (aggregated)
    print("\n" + "=" * 60)
    print("8. ACTUAL AGGREGATED QUERY (what InsightsService does)")
    print("=" * 60)
    cur.execute("""
        SELECT
            business_category,
            SUM(COALESCE(competition_count, 0)),
            SUM(demand_score * COALESCE(NULLIF(competition_count, 0), 1))
                / NULLIF(SUM(COALESCE(NULLIF(competition_count, 0), 1)), 0),
            SUM(competition_score * COALESCE(NULLIF(competition_count, 0), 1))
                / NULLIF(SUM(COALESCE(NULLIF(competition_count, 0), 1)), 0),
            SUM(average_market_price * COALESCE(NULLIF(competition_count, 0), 1))
                / NULLIF(SUM(CASE WHEN average_market_price IS NOT NULL THEN COALESCE(NULLIF(competition_count, 0), 1) ELSE 0 END), 0),
            SUM(opportunity_score * COALESCE(NULLIF(competition_count, 0), 1))
                / NULLIF(SUM(COALESCE(NULLIF(competition_count, 0), 1)), 0),
            MAX(data_date),
            COUNT(*)
        FROM location_business_metrics
        WHERE location_id = %s
          AND LOWER(business_category) = 'food processing'
          AND COALESCE(data_source, '') <> 'UdyamSetu development seed'
        GROUP BY business_category
    """, (str(location_id),))

    agg_row = cur.fetchone()
    print(f"  Aggregated result:")
    print(f"    Category: {agg_row[0]}")
    print(f"    competition_count (SUM): {agg_row[1]}")
    print(f"    demand_score (weighted avg): {agg_row[2]}")
    print(f"    competition_score (weighted avg): {agg_row[3]}")
    print(f"    average_market_price (weighted avg): {agg_row[4]}")
    print(f"    opportunity_score (weighted avg): {agg_row[5]}")
    print(f"    data_date: {agg_row[6]}")
    print(f"    row_count: {agg_row[7]}")

    conn.close()
    print("\n" + "=" * 60)
    print("DEBUG COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()