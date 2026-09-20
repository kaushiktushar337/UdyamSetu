from pathlib import Path
import pandas as pd


DATA = Path(__file__).resolve().parents[1] / "data" / "ises" / "India-2022-ESIS-full-data.dta"


def test_ises_dataset_shape_and_cities():
    df = pd.read_stata(DATA, convert_categoricals=True)
    assert df.shape == (10672, 196)
    assert set(df["city"].dropna().astype(str).str.strip()) == {
        "Hyderabad", "Jaipur", "Kochi", "Ludhiana", "Mumbai",
        "Sehore", "Surat", "Tezpur", "Varanasi",
    }


def test_ises_required_fields_and_weight():
    df = pd.read_stata(DATA, convert_categoricals=True)
    required = {
        "wstrict", "d6", "n7", "l1a", "l1b", "k10", "k12", "k17",
        "ir1a", "ir1b", "ir1e", "ir6", "ir7", "c31", "c31a", "c32",
        "c38", "c42a", "c42c", "d13a", "r5", "a4m", "a4r", "a4s",
    }
    assert required.issubset(df.columns)
    weights = pd.to_numeric(df["wstrict"], errors="coerce")
    assert weights.notna().mean() > 0.99
    assert (weights > 0).mean() > 0.99


def test_ises_profit_values_are_labelled_categories():
    df = pd.read_stata(DATA, convert_categoricals=True)
    values = set(df["n7"].dropna().astype(str).str.strip())
    assert "Profit" in values
    assert "Loss" in values
    assert "Zero profit" in values


def test_ises_loader_builds_all_27_city_sector_metrics():
    import importlib.util
    import sys
    import types

    sys.modules.setdefault("psycopg2", types.ModuleType("psycopg2"))
    spec = importlib.util.spec_from_file_location(
        "load_ises_test",
        Path(__file__).resolve().parents[1] / "database" / "load_ises.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    df = pd.read_stata(DATA, convert_categoricals=True)
    built = []
    for city in module.CITY_MAP:
        city_df = df[df["city"].astype(str).str.strip().eq(city)]
        for sector, column in module.SECTOR_COLUMNS.items():
            metric = module.build_metrics(city_df, city, sector, column)
            assert metric is not None
            assert 0 <= metric["profit_business_pct"] <= 100
            assert metric["weighted_businesses"] > 0
            built.append(metric)

    assert len(built) == 27
