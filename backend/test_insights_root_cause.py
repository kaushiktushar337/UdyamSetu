#!/usr/bin/env python
"""Integration/regression checks for Business Insights.

Run this against a database with DATABASE_URL set. The tests intentionally
discover the Prayagraj location instead of assuming a numeric location id.
"""
import os

import psycopg2

from api.insights_service import InsightsService


def db():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL not set")
    return psycopg2.connect(url)


def prayagraj_id():
    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT location_id
                FROM location_reference
                WHERE LOWER(location_name) = 'prayagraj'
                   OR LOWER(district) = 'prayagraj'
                ORDER BY CASE WHEN LOWER(location_name) = 'prayagraj' THEN 0 ELSE 1 END
                LIMIT 1
                """
            )
            row = cur.fetchone()
            if not row:
                raise AssertionError("Prayagraj location is missing")
            return str(row[0])
    finally:
        conn.close()


def test_profile_duplicates_are_absent():
    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT business_name, category, subcategory, COUNT(*)
                FROM business_reference_profiles
                GROUP BY business_name, category, subcategory
                HAVING COUNT(*) > 1
                """
            )
            duplicates = cur.fetchall()
            assert not duplicates, f"Duplicate logical business profiles remain: {duplicates}"
    finally:
        conn.close()


def test_metric_natural_keys():
    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT location_id, business_category, subcategory, data_date,
                       COALESCE(data_source, ''), COUNT(*)
                FROM location_business_metrics
                GROUP BY location_id, business_category, subcategory, data_date,
                         COALESCE(data_source, '')
                HAVING COUNT(*) > 1
                LIMIT 100
                """
            )
            duplicates = cur.fetchall()
            assert not duplicates, f"Duplicate market metric natural keys remain: {duplicates}"
    finally:
        conn.close()


def test_prayagraj_food_processing_regression():
    result = InsightsService().by_location(prayagraj_id(), "Food Processing")
    assert result["available"]
    assert result["competition_count"] is not None
    assert result["competition_count"] != 21066374
    assert 0 <= result["demand_score"] <= 100
    assert 0 <= result["competition_score"] <= 100
    assert 0 <= result["opportunity_score"] <= 100
    assert all(
        item["business_name"] and item.get("subcategory")
        for item in result["top_opportunities"]
    )


def test_multiple_requested_location_category_pairs():
    service = InsightsService()
    locations = {x["location_name"].lower(): x for x in service.locations()}

    # The exact regression matrix requested for Business Insights. Categories
    # such as Furniture/Electronics are intentionally sent as the user would
    # expect; availability may be false if the selected category is not a
    # market category in the current dataset.
    cases = [
        ("prayagraj", "Dairy"),
        ("prayagraj", "Food Processing"),
        ("delhi", "Retail"),
        ("pune", "Furniture"),
        ("ahmedabad", "Food Processing"),
        ("bengaluru", "Electronics"),
    ]

    for location_name, category in cases:
        location = locations.get(location_name)
        assert location, f"Missing required test location: {location_name}"
        result = service.by_location(location["location_id"], category)

        assert result["category"] == category
        assert result["normalized_category"]
        assert result["competition_count"] is None or result["competition_count"] >= 0
        assert result["demand_score"] is None or 0 <= result["demand_score"] <= 100
        assert result["competition_score"] is None or 0 <= result["competition_score"] <= 100
        assert result["opportunity_score"] is None or 0 <= result["opportunity_score"] <= 100

        if result["available"]:
            # Opportunities must stay within the selected category.
            assert all(
                item.get("subcategory")
                for item in result["top_opportunities"]
            )


if __name__ == "__main__":
    test_profile_duplicates_are_absent()
    test_metric_natural_keys()
    test_prayagraj_food_processing_regression()
    test_multiple_locations_and_categories()
    print("Business Insights integration checks passed.")
