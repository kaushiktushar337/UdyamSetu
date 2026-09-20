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
                "processing",
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
                    result["data_date"] = (
                        result["data_date"].isoformat()
                    )

                return result

        finally:
            conn.close()