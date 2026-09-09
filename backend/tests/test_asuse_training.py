from pathlib import Path
import json
import pandas as pd

from ml_engine.training.asuse_pipeline import FEATURE_COLUMNS, load_training_frame

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "asuse_2023_24_training.csv"


def test_asuse_training_frame_exists_and_is_establishment_level():
    assert DATA.exists()
    df = pd.read_csv(DATA, nrows=1000)
    required = set(FEATURE_COLUMNS + ["net_surplus", "profitable", "profitability_tier"])
    assert required.issubset(df.columns)
    assert df["key"].is_unique
    assert set(df["profitability_tier"].dropna().unique()) <= {"low", "medium", "high"}


def test_tier_target_is_balanced_enough_for_training():
    df = pd.read_csv(DATA, usecols=["profitability_tier"])
    counts = df["profitability_tier"].value_counts()
    assert len(counts) == 3
    assert counts.min() / counts.max() > 0.95
