from __future__ import annotations

import os
from typing import Any, Optional

import psycopg2


class ISESService:

    def __init__(
        self,
        database_url: str | None = None,
    ):
        self.database_url = (
            database_url
            or os.getenv("DATABASE_URL")
        )

    def _connect(self):
        if not self.database_url:
            raise RuntimeError(
                "DATABASE_URL is missing"
            )

        return psycopg2.connect(
            self.database_url
        )

    @staticmethod
    def category_to_sector(
        category: str,
    ) -> Optional[str]:

        value = (category or "").lower()

        if any(
            x in value
            for x in [
                "manufacturing",
                "food processing",
                "rural manufacturing",
                "agriculture",
                "agriculture allied",
                "processing",
                "food",
                "dairy",
                "bakery",
                "garments",
                "furniture",
                "handicraft",
            ]
        ):
            return "Production"

        if any(
            x in value
            for x in [
                "retail",
                "trading",
                "shop",
                "reselling",
            ]
        ):
            return "Retail"

        if any(
            x in value
            for x in [
                "service",
                "repair",
                "design",
                "salon",
                "parlour",
                "digital",
            ]
        ):
            return "Other Services"

        return None

    @staticmethod
    def environment_score(metrics: dict[str, Any]) -> Optional[float]:
        """Build a 0-100 business-environment signal from available ISES indicators.

        This is an internal UdyamSetu composite, not an official survey indicator.
        Components are renormalized when a metric is unavailable.
        """
        groups = [
            ("profit_business_pct", 0.30, False),
            ("bank_account_pct", 0.10, False),
            ("business_loan_pct", 0.10, False),
            ("competitor_monitoring_pct", 0.08, False),
            ("customer_feedback_pct", 0.08, False),
            ("supplier_market_info_pct", 0.08, False),
            ("monthly_budget_pct", 0.08, False),
            ("sales_target_pct", 0.08, False),
            ("computer_use_pct", 0.04, False),
            ("smartphone_use_pct", 0.04, False),
            ("electricity_grid_pct", 0.05, False),
            ("water_use_pct", 0.03, False),
            ("power_outage_pct", 0.02, True),
        ]
        numerator = 0.0
        denominator = 0.0
        for name, weight, inverse in groups:
            value = metrics.get(name)
            if value is None:
                continue
            try:
                score = max(0.0, min(100.0, float(value)))
            except (TypeError, ValueError):
                continue
            if inverse:
                score = 100.0 - score
            numerator += score * weight
            denominator += weight
        if denominator <= 0:
            return None
        return round(numerator / denominator, 2)

    def get_for_location(
        self,
        location_id: str,
        category: str,
    ) -> Optional[dict[str, Any]]:

        sector = self.category_to_sector(category)

        if sector is None:
            return None

        conn = self._connect()

        try:

            with conn.cursor() as cur:

                cur.execute(
                    """
                    SELECT
                        city,
                        sector,
                        weighted_businesses,
                        avg_regular_month_sales,
                        profit_business_pct,
                        avg_workers,
                        paid_worker_pct,
                        bank_account_pct,
                        business_loan_pct,
                        loan_application_pct,
                        competitor_monitoring_pct,
                        customer_feedback_pct,
                        supplier_market_info_pct,
                        monthly_budget_pct,
                        sales_target_pct,
                        electricity_use_pct,
                        electricity_grid_pct,
                        power_outage_pct,
                        water_use_pct,
                        computer_use_pct,
                        smartphone_use_pct,
                        contractual_input_purchase_pct,
                        informal_payment_pct,
                        data_source,
                        data_date
                    FROM ises_city_sector_metrics
                    WHERE location_id = %s
                      AND sector = %s
                    ORDER BY data_date DESC
                    LIMIT 1
                    """,
                    (
                        location_id,
                        sector,
                    ),
                )

                row = cur.fetchone()

                if not row:
                    return None

                fields = [
                    "city",
                    "sector",
                    "weighted_businesses",
                    "avg_regular_month_sales",
                    "profit_business_pct",
                    "avg_workers",
                    "paid_worker_pct",
                    "bank_account_pct",
                    "business_loan_pct",
                    "loan_application_pct",
                    "competitor_monitoring_pct",
                    "customer_feedback_pct",
                    "supplier_market_info_pct",
                    "monthly_budget_pct",
                    "sales_target_pct",
                    "electricity_use_pct",
                    "electricity_grid_pct",
                    "power_outage_pct",
                    "water_use_pct",
                    "computer_use_pct",
                    "smartphone_use_pct",
                    "contractual_input_purchase_pct",
                    "informal_payment_pct",
                    "data_source",
                    "data_date",
                ]

                result = dict(
                    zip(fields, row)
                )

                if result["data_date"]:
                    result["data_date"] = result["data_date"].isoformat()

                result["environment_score"] = self.environment_score(result)
                result.pop("data_source", None)
                return result

        finally:
            conn.close()