from __future__ import annotations

import argparse
import json
import os
import zipfile
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd

KEY_COLS = ["fsu_serial_no", "sample_est_no", "second_stage_stratum", "segment_no"]

FEATURE_COLUMNS = [
    "sector", "district", "location", "major_nic_2dig", "major_nic_5dig",
    "ownership_type", "education_level", "technical_training", "num_eco_activities",
    "bank_account", "est_type", "years_of_operation", "months_operated",
    "daily_work_hours", "accounts_maintained", "used_computer", "used_internet",
    "registered", "manuf_services", "contract_manuf_service", "franchise",
    "total_workers", "fixed_assets_owned", "fixed_assets_hired", "net_additions_assets",
]

NUMERIC_FEATURES = [
    "years_of_operation", "months_operated", "daily_work_hours", "num_eco_activities",
    "total_workers", "fixed_assets_owned", "fixed_assets_hired", "net_additions_assets",
]
CATEGORICAL_FEATURES = [c for c in FEATURE_COLUMNS if c not in NUMERIC_FEATURES]


def _norm_key(df: pd.DataFrame) -> pd.Series:
    cols = []
    for name in KEY_COLS:
        if name in df.columns:
            cols.append(name)
            continue
        aliases = {
            "second_stage_stratum": ["second_stage_stratum_no"],
            "sample_est_no": ["sample_estab_no"],
        }
        found = next((a for a in aliases.get(name, []) if a in df.columns), None)
        if found is None:
            raise KeyError(f"Cannot build establishment key: missing {name!r} in columns {list(df.columns)}")
        cols.append(found)
    return df[cols].astype(str).fillna("").agg("|".join, axis=1)


def _read_member(z: zipfile.ZipFile, pattern: str) -> str:
    matches = [n for n in z.namelist() if n.lower().endswith(".csv") and pattern.lower() in n.lower()]
    if not matches:
        raise FileNotFoundError(f"No CSV member matching {pattern!r} found in archive")
    return matches[0]


def _stream_target(z: zipfile.ZipFile, chunksize: int = 200_000) -> pd.DataFrame:
    name = _read_member(z, "LEVEL - 16")
    parts = []
    with z.open(name) as f:
        for chunk in pd.read_csv(f, chunksize=chunksize):
            chunk = chunk[chunk["item_no_14"].astype(str) == "1402"].copy()
            if chunk.empty:
                continue
            chunk["key"] = _norm_key(chunk)
            chunk["net_surplus"] = pd.to_numeric(chunk["amount_14"], errors="coerce")
            parts.append(chunk[["key", "net_surplus"]])
    target = pd.concat(parts, ignore_index=True)
    target = target.dropna(subset=["key", "net_surplus"])
    # One target row per establishment is expected. If duplicates occur, retain the first.
    target = target.drop_duplicates("key", keep="first")
    return target


def _stream_level2(z: zipfile.ZipFile, chunksize: int = 150_000) -> pd.DataFrame:
    name = _read_member(z, "LEVEL - 02")
    keep = [
        "fsu_serial_no", "sample_est_no", "second_stage_stratum_no", "segment_no",
        "sector", "district", "location", "major_nic_2dig", "major_nic_5dig",
        "ownership_type", "education_level", "technical_training", "num_eco_activities",
        "bank_account", "est_type", "years_of_operation", "months_operated",
        "daily_work_hours", "accounts_maintained", "used_computer", "used_internet",
        "registered", "manuf_services", "contract_manuf_service", "franchise",
    ]
    first_parts = []
    activity_counts: Dict[str, int] = {}
    with z.open(name) as f:
        for chunk in pd.read_csv(f, chunksize=chunksize, low_memory=False):
            chunk["key"] = _norm_key(chunk)
            for key, n in chunk["key"].value_counts().items():
                activity_counts[key] = activity_counts.get(key, 0) + int(n)
            first_parts.append(chunk[keep + ["key"]])
    base = pd.concat(first_parts, ignore_index=True)
    base = base.drop_duplicates("key", keep="first")
    base["num_activity_records"] = base["key"].map(activity_counts).fillna(1).astype(float)
    return base


def _stream_workers(z: zipfile.ZipFile, chunksize: int = 200_000) -> pd.DataFrame:
    name = _read_member(z, "LEVEL - 09")
    parts = []
    with z.open(name) as f:
        for chunk in pd.read_csv(f, chunksize=chunksize, low_memory=False):
            chunk = chunk[chunk["item_no"].astype(str) == "789"].copy()
            if chunk.empty:
                continue
            chunk["key"] = _norm_key(chunk)
            chunk["total_workers"] = pd.to_numeric(chunk["total_workers"], errors="coerce")
            parts.append(chunk[["key", "total_workers"]])
    if not parts:
        return pd.DataFrame(columns=["key", "total_workers"])
    out = pd.concat(parts, ignore_index=True)
    return out.groupby("key", as_index=False)["total_workers"].first()


def _stream_assets(z: zipfile.ZipFile, chunksize: int = 200_000) -> pd.DataFrame:
    name = _read_member(z, "LEVEL - 11")
    parts = []
    with z.open(name) as f:
        for chunk in pd.read_csv(f, chunksize=chunksize, low_memory=False):
            chunk = chunk[chunk["item_no"].astype(str) != "1019"].copy()
            if chunk.empty:
                continue
            chunk["key"] = _norm_key(chunk)
            for col in ["mv_assets_owned", "mv_assets_hired", "net_additions_owned"]:
                chunk[col] = pd.to_numeric(chunk[col], errors="coerce").fillna(0)
            g = chunk.groupby("key", as_index=False)[["mv_assets_owned", "mv_assets_hired", "net_additions_owned"]].sum()
            parts.append(g)
    if not parts:
        return pd.DataFrame(columns=["key", "fixed_assets_owned", "fixed_assets_hired", "net_additions_assets"])
    out = pd.concat(parts, ignore_index=True).groupby("key", as_index=False).sum()
    return out.rename(columns={
        "mv_assets_owned": "fixed_assets_owned",
        "mv_assets_hired": "fixed_assets_hired",
        "net_additions_owned": "net_additions_assets",
    })


def build_establishment_dataset(raw_zip: str | Path, output_csv: str | Path, chunksize: int = 150_000) -> Dict[str, int]:
    raw_zip = Path(raw_zip)
    output_csv = Path(output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(raw_zip) as z:
        target = _stream_target(z, chunksize=max(chunksize, 100_000))
        base = _stream_level2(z, chunksize=chunksize)
        workers = _stream_workers(z, chunksize=max(chunksize, 100_000))
        assets = _stream_assets(z, chunksize=max(chunksize, 100_000))

    data = target.merge(base, on="key", how="inner", validate="one_to_one")
    data = data.merge(workers, on="key", how="left", validate="one_to_one")
    data = data.merge(assets, on="key", how="left", validate="one_to_one")
    data["total_workers"] = data["total_workers"].fillna(0)
    for c in ["fixed_assets_owned", "fixed_assets_hired", "net_additions_assets"]:
        data[c] = data[c].fillna(0)
    data["profitable"] = (data["net_surplus"] > 0).astype(int)
    # The raw positive/negative target is extremely imbalanced in this survey.
    # A second target provides a more useful balanced supervised-learning task:
    # relative net-surplus tier within the observed ASUSE establishments.
    q1, q2 = data["net_surplus"].quantile([1/3, 2/3]).tolist()
    data["profitability_tier"] = pd.cut(
        data["net_surplus"], bins=[-np.inf, q1, q2, np.inf], labels=["low", "medium", "high"], include_lowest=True
    ).astype(str)
    data["dataset_source"] = "ASUSE 2023-24"
    data["is_synthetic"] = False
    data.to_csv(output_csv, index=False)
    return {
        "rows": int(len(data)),
        "positive": int(data["profitable"].sum()),
        "negative": int((1 - data["profitable"]).sum()),
        "tier_counts": data["profitability_tier"].value_counts().to_dict(),
        "features": len(FEATURE_COLUMNS),
    }


def load_training_frame(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)
    missing = [c for c in FEATURE_COLUMNS + ["profitable"] if c not in df.columns]
    if missing:
        raise ValueError(f"Training dataset missing columns: {missing}")
    return df


def cli() -> None:
    parser = argparse.ArgumentParser(description="Build an establishment-level ASUSE 2023-24 ML dataset.")
    parser.add_argument("raw_zip")
    parser.add_argument("--output", default="data/asuse_2023_24_training.csv")
    parser.add_argument("--chunksize", type=int, default=150_000)
    args = parser.parse_args()
    result = build_establishment_dataset(args.raw_zip, args.output, args.chunksize)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    cli()
