from __future__ import annotations

import math
import os
from typing import Any

import requests


class LocationService:
    """Resolve browser GPS to an application location and save the capture."""

    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or os.getenv("DATABASE_URL")
        self.max_distance_km = float(os.getenv("LOCATION_MATCH_MAX_KM", "50"))
        self.reverse_geocode = os.getenv("LOCATION_REVERSE_GEOCODE", "true").lower() in {"1", "true", "yes"}

    def _connect(self):
        if not self.database_url:
            return None
        import psycopg2
        return psycopg2.connect(self.database_url)

    @staticmethod
    def _distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        r = 6371.0088
        p1, p2 = math.radians(lat1), math.radians(lat2)
        dp = math.radians(lat2 - lat1)
        dl = math.radians(lon2 - lon1)
        a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
        return 2 * r * math.asin(math.sqrt(a))

    def _reference_locations(self) -> list[dict[str, Any]]:
        conn = self._connect()
        if conn is None:
            return []
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT location_id, location_name, state, district, latitude, longitude
                       FROM location_reference
                       WHERE latitude IS NOT NULL AND longitude IS NOT NULL"""
                )
                return [
                    {
                        "location_id": str(r[0]),
                        "location_name": r[1] or "",
                        "state": r[2] or "",
                        "district": r[3] or "",
                        "latitude": float(r[4]),
                        "longitude": float(r[5]),
                    }
                    for r in cur.fetchall()
                ]
        finally:
            conn.close()

    def resolve(self, latitude: float, longitude: float) -> dict[str, Any]:
        refs = self._reference_locations()
        nearest = None
        if refs:
            nearest = min(
                refs,
                key=lambda x: self._distance_km(latitude, longitude, x["latitude"], x["longitude"]),
            )
            nearest = {**nearest, "distance_km": round(self._distance_km(latitude, longitude, nearest["latitude"], nearest["longitude"]), 2)}
            if nearest["distance_km"] > self.max_distance_km:
                nearest = None

        estimated_address = None
        if nearest:
            parts = [nearest["location_name"], nearest["district"], nearest["state"]]
            estimated_address = ", ".join(dict.fromkeys(p for p in parts if p))

        if not estimated_address and self.reverse_geocode:
            try:
                response = requests.get(
                    "https://nominatim.openstreetmap.org/reverse",
                    params={"lat": latitude, "lon": longitude, "format": "jsonv2", "zoom": 12, "addressdetails": 1},
                    headers={"User-Agent": "UdyamSetu/1.0 local-development"},
                    timeout=5,
                )
                if response.ok:
                    address = response.json().get("address", {})
                    parts = [
                        address.get("village") or address.get("town") or address.get("city") or address.get("municipality"),
                        address.get("county") or address.get("district"),
                        address.get("state"),
                    ]
                    estimated_address = ", ".join(dict.fromkeys(p for p in parts if p)) or response.json().get("display_name")
            except requests.RequestException:
                pass

        return {
            "location_id": nearest["location_id"] if nearest else None,
            "estimated_address": estimated_address or "Location detected, but an address could not be estimated",
            "distance_km": nearest["distance_km"] if nearest else None,
            "matched": nearest is not None,
        }

    def save_capture(self, user_id: str | None, latitude: float, longitude: float, accuracy: float | None, resolution: dict[str, Any]) -> bool:
        if not self.database_url or not user_id:
            return False
        conn = self._connect()
        if conn is None:
            return False
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO user_locations
                       (user_id, latitude, longitude, accuracy, location_id, location_text, source)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (
                        user_id,
                        latitude,
                        longitude,
                        accuracy,
                        resolution.get("location_id"),
                        resolution.get("estimated_address"),
                        "browser_geolocation",
                    ),
                )
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False
        finally:
            conn.close()

    def latest(self, user_id: str) -> dict[str, Any] | None:
        if not self.database_url:
            return None
        conn = self._connect()
        if conn is None:
            return None
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT location_id, location_text, accuracy, captured_at
                       FROM user_locations
                       WHERE user_id = %s
                       ORDER BY captured_at DESC
                       LIMIT 1""",
                    (user_id,),
                )
                row = cur.fetchone()
                if not row:
                    return None
                return {
                    "location_id": str(row[0]) if row[0] is not None else None,
                    "estimated_address": row[1],
                    "accuracy_m": float(row[2]) if row[2] is not None else None,
                    "captured_at": row[3].isoformat() if row[3] else None,
                }
        finally:
            conn.close()
