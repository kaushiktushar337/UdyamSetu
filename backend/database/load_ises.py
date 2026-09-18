from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import pandas as pd
import psycopg2
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

ISES_FILE = Path(
    os.getenv(
        "ISES_DATA_FILE",
        "data/ises/India-2022-ESIS-full-data.dta"
    )
)

DATA_DATE = "2022-04-30"


CITY_MAP = {
    "Hyderabad": "Hyderabad",
    "Jaipur": "Jaipur",
    "Kochi": "Kochi",
    "Ludhiana": "Ludhiana",
    "Mumbai": "Mumbai",
    "Sehore": "Sehore",
    "Surat": "Surat",
    "Tezpur": "Tezpur",
    "Varanasi": "Varanasi",
}


SECTOR_COLUMNS = {
    "Production": "a4m",
    "Retail": "a4r",
    "Other Services": "a4s",
}


def clean_numeric(series: pd.Series) -> pd.Series:
    """
    Convert labelled Stata columns into numeric values.

    Invalid / Don't know values become NaN.
    """
    return pd.to_numeric(series, errors="coerce")


def yes_rate(
    df: pd.DataFrame,
    column: str,
    mask: Optional[pd.Series] = None,
) -> Optional[float]:
    """
    Weighted percentage answering Yes.
    Uses wstrict because the strict weight represents confirmed
    informal businesses.
    """
    work = df

    if mask is not None:
        work = work.loc[mask]

    if work.empty:
        return None

    values = work[column].astype(str).str.strip()

    valid = values.isin(["Yes", "No"])

    work = work.loc[valid]
    values = values.loc[valid]

    if work.empty:
        return None

    weights = clean_numeric(work["wstrict"])

    valid_weight = weights.notna()

    if not valid_weight.any():
        return None

    weights = weights.loc[valid_weight]
    values = values.loc[valid_weight]

    denominator = weights.sum()

    if denominator <= 0:
        return None

    numerator = weights.loc[values == "Yes"].sum()

    return round(float(numerator / denominator * 100), 2)


def weighted_mean(
    df: pd.DataFrame,
    value_column: str,
) -> Optional[float]:

    values = clean_numeric(df[value_column])
    weights = clean_numeric(df["wstrict"])

    valid = values.notna() & weights.notna() & (weights > 0)

    if not valid.any():
        return None

    values = values.loc[valid]
    weights = weights.loc[valid]

    denominator = weights.sum()

    if denominator <= 0:
        return None

    return round(float((values * weights).sum() / denominator), 2)


def weighted_count(df: pd.DataFrame) -> Optional[float]:

    weights = clean_numeric(df["wstrict"])

    weights = weights.dropna()

    if weights.empty:
        return None

    return round(float(weights.sum()), 2)


def category_rate(
    df: pd.DataFrame,
    column: str,
    target: str,
) -> Optional[float]:
    """Weighted percentage for a labelled categorical response."""
    values = df[column].astype(str).str.strip()
    weights = clean_numeric(df["wstrict"])

    valid = (
        values.notna()
        & ~values.isin(["", "nan", "NaN", "Don't know (spontaneous)", "Refusal (spontaneous)"])
        & weights.notna()
        & (weights > 0)
    )
    if not valid.any():
        return None

    values = values.loc[valid]
    weights = weights.loc[valid]
    denominator = weights.sum()
    if denominator <= 0:
        return None

    numerator = weights.loc[values.eq(target)].sum()
    return round(float(numerator / denominator * 100), 2)


def sector_mask(
    df: pd.DataFrame,
    sector_column: str,
) -> pd.Series:

    values = df[sector_column].astype(str).str.strip()

    return (
        values.notna()
        & ~values.isin([
            "",
            "nan",
            "NaN",
            "-9",
            "Don't know (spontaneous)",
        ])
    )

def category_rate(
    df: pd.DataFrame,
    column: str,
    target: str,
) -> Optional[float]:

    values = df[column].astype(str).str.strip()
    weights = clean_numeric(df["wstrict"])

    valid = (
        values.notna()
        & ~values.isin([
            "",
            "nan",
            "NaN",
            "Don't know (spontaneous)",
        ])
        & weights.notna()
        & (weights > 0)
    )

    if not valid.any():
        return None

    values = values.loc[valid]
    weights = weights.loc[valid]

    denominator = weights.sum()

    if denominator <= 0:
        return None

    numerator = weights.loc[
        values.eq(target)
    ].sum()

    return round(
        float(numerator / denominator * 100),
        2,
    )
def build_metrics(
    city_df: pd.DataFrame,
    city: str,
    sector: str,
    sector_column: str,
):

    mask = sector_mask(city_df, sector_column)
    df = city_df.loc[mask].copy()

    if df.empty:
        return None

    avg_workers = None

    l1a = clean_numeric(df["l1a"])
    l1b = clean_numeric(df["l1b"])

    worker_mask = l1a.notna() & l1b.notna()

    if worker_mask.any():
        workers = l1a.loc[worker_mask] + l1b.loc[worker_mask]
        weights = clean_numeric(df.loc[worker_mask, "wstrict"])

        valid = weights.notna() & (weights > 0)

        if valid.any():
            workers = workers.loc[valid]
            weights = weights.loc[valid]

            avg_workers = round(
                float((workers * weights).sum() / weights.sum()),
                2,
            )

    paid_worker_pct = None

    if worker_mask.any():
        paid = l1a.loc[worker_mask]
        unpaid = l1b.loc[worker_mask]
        total = paid + unpaid

        valid = total > 0

        if valid.any():
            weights = clean_numeric(
                df.loc[worker_mask, "wstrict"]
            )

            valid = valid & weights.notna() & (weights > 0)

            if valid.any():
                paid_worker_pct = round(
                    float(
                        (
                            (
                                paid.loc[valid]
                                / total.loc[valid]
                            )
                            * weights.loc[valid]
                        ).sum()
                        / weights.loc[valid].sum()
                        * 100
                    ),
                    2,
                )

    electricity_mask = (
        df["c31"]
        .astype(str)
        .str.strip()
        .eq("Yes")
    )

    return {
        "city": city,
        "sector": sector,

        "weighted_businesses":
            weighted_count(df),

        "avg_regular_month_sales":
            weighted_mean(df, "d6"),

        "profit_business_pct":
            category_rate(
                df,
                "n7",
                "Profit",
            ),
        "avg_workers":
            avg_workers,

        "paid_worker_pct":
            paid_worker_pct,

        "bank_account_pct":
            yes_rate(df, "k10"),

        "business_loan_pct":
            yes_rate(df, "k12"),

        "loan_application_pct":
            yes_rate(df, "k17"),

        "competitor_monitoring_pct":
            yes_rate(df, "ir1a"),

        "customer_feedback_pct":
            yes_rate(df, "ir1b"),

        "supplier_market_info_pct":
            yes_rate(df, "ir1e"),

        "monthly_budget_pct":
            yes_rate(df, "ir6"),

        "sales_target_pct":
            yes_rate(df, "ir7"),

        "electricity_use_pct":
            yes_rate(df, "c31"),

        "electricity_grid_pct":
            yes_rate(
                df,
                "c31a",
                electricity_mask,
            ),

        "power_outage_pct":
            yes_rate(
                df,
                "c32",
                electricity_mask,
            ),

        "water_use_pct":
            yes_rate(df, "c38"),

        "computer_use_pct":
            yes_rate(df, "c42a"),

        "smartphone_use_pct":
            yes_rate(df, "c42c"),

        "contractual_input_purchase_pct":
            yes_rate(df, "d13a"),

        "informal_payment_pct":
            yes_rate(df, "r5"),
    }


def resolve_location_id(
    conn,
    city: str,
) -> Optional[str]:

    with conn.cursor() as cur:

        cur.execute(
            """
            SELECT location_id
            FROM location_reference
            WHERE LOWER(location_name) = LOWER(%s)
            LIMIT 1
            """,
            (city,),
        )

        row = cur.fetchone()

        if row:
            return str(row[0])

        cur.execute(
            """
            SELECT location_id
            FROM location_reference
            WHERE LOWER(district) = LOWER(%s)
            LIMIT 1
            """,
            (city,),
        )

        row = cur.fetchone()

        return str(row[0]) if row else None


def insert_metric(
    conn,
    location_id: str,
    metric: dict,
):

    with conn.cursor() as cur:

        cur.execute(
            """
            INSERT INTO ises_city_sector_metrics (
                location_id,
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
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s
            )
            ON CONFLICT (location_id, sector, data_date)
            DO UPDATE SET
                city = EXCLUDED.city,
                weighted_businesses = EXCLUDED.weighted_businesses,
                avg_regular_month_sales = EXCLUDED.avg_regular_month_sales,
                profit_business_pct = EXCLUDED.profit_business_pct,
                avg_workers = EXCLUDED.avg_workers,
                paid_worker_pct = EXCLUDED.paid_worker_pct,
                bank_account_pct = EXCLUDED.bank_account_pct,
                business_loan_pct = EXCLUDED.business_loan_pct,
                loan_application_pct = EXCLUDED.loan_application_pct,
                competitor_monitoring_pct = EXCLUDED.competitor_monitoring_pct,
                customer_feedback_pct = EXCLUDED.customer_feedback_pct,
                supplier_market_info_pct = EXCLUDED.supplier_market_info_pct,
                monthly_budget_pct = EXCLUDED.monthly_budget_pct,
                sales_target_pct = EXCLUDED.sales_target_pct,
                electricity_use_pct = EXCLUDED.electricity_use_pct,
                electricity_grid_pct = EXCLUDED.electricity_grid_pct,
                power_outage_pct = EXCLUDED.power_outage_pct,
                water_use_pct = EXCLUDED.water_use_pct,
                computer_use_pct = EXCLUDED.computer_use_pct,
                smartphone_use_pct = EXCLUDED.smartphone_use_pct,
                contractual_input_purchase_pct = EXCLUDED.contractual_input_purchase_pct,
                informal_payment_pct = EXCLUDED.informal_payment_pct,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                location_id,
                metric["city"],
                metric["sector"],
                metric["weighted_businesses"],
                metric["avg_regular_month_sales"],
                metric["profit_business_pct"],
                metric["avg_workers"],
                metric["paid_worker_pct"],
                metric["bank_account_pct"],
                metric["business_loan_pct"],
                metric["loan_application_pct"],
                metric["competitor_monitoring_pct"],
                metric["customer_feedback_pct"],
                metric["supplier_market_info_pct"],
                metric["monthly_budget_pct"],
                metric["sales_target_pct"],
                metric["electricity_use_pct"],
                metric["electricity_grid_pct"],
                metric["power_outage_pct"],
                metric["water_use_pct"],
                metric["computer_use_pct"],
                metric["smartphone_use_pct"],
                metric["contractual_input_purchase_pct"],
                metric["informal_payment_pct"],
                "World Bank ISES 2022",
                DATA_DATE,
            ),
        )


def main():

    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL is missing"
        )

    if not ISES_FILE.exists():
        raise FileNotFoundError(
            f"ISES dataset not found: {ISES_FILE}"
        )

    print(f"Loading ISES dataset: {ISES_FILE}")

    df = pd.read_stata(
        ISES_FILE,
        convert_categoricals=True,
    )

    required_columns = {
        "city",
        "wstrict",
        "d6",
        "n7",
        "l1a",
        "l1b",
        "k10",
        "k12",
        "k17",
        "ir1a",
        "ir1b",
        "ir1e",
        "ir6",
        "ir7",
        "c31",
        "c31a",
        "c32",
        "c38",
        "c42a",
        "c42c",
        "d13a",
        "r5",
        "a4m",
        "a4r",
        "a4s",
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise RuntimeError(
            "ISES dataset is missing columns: "
            + ", ".join(sorted(missing))
        )

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns):,}")

    conn = psycopg2.connect(DATABASE_URL)

    try:

        inserted = 0

        for city in CITY_MAP:

            city_df = df[
                df["city"]
                .astype(str)
                .str.strip()
                .eq(city)
            ].copy()

            if city_df.empty:
                print(
                    f"WARNING: no records found for {city}"
                )
                continue

            location_id = resolve_location_id(
                conn,
                city,
            )

            if location_id is None:
                print(
                    f"WARNING: location_reference "
                    f"does not contain {city}"
                )
                continue

            for sector, column in SECTOR_COLUMNS.items():

                metric = build_metrics(
                    city_df,
                    city,
                    sector,
                    column,
                )

                if metric is None:
                    continue

                insert_metric(
                    conn,
                    location_id,
                    metric,
                )

                inserted += 1

                print(
                    f"Loaded: {city} / {sector}"
                )

        conn.commit()

        print()
        print(
            f"ISES load complete. "
            f"Rows written: {inserted}"
        )

    except Exception:

        conn.rollback()
        raise

    finally:

        conn.close()


if __name__ == "__main__":
    main()