from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, balanced_accuracy_score, classification_report, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .asuse_pipeline import CATEGORICAL_FEATURES, FEATURE_COLUMNS, NUMERIC_FEATURES, load_training_frame


def train(data_path: str, model_path: str, metrics_path: str, test_size: float = 0.2, sample_size: int | None = None, random_state: int = 42, trees: int = 200, target: str = "profitability_tier"):
    df = load_training_frame(data_path)
    if target not in df.columns:
        raise ValueError(f"Unknown target {target!r}. Available targets: profitable, profitability_tier")
    if sample_size and sample_size < len(df):
        df = df.sample(sample_size, random_state=random_state)
    X = df[FEATURE_COLUMNS].copy()
    y = df[target].copy()

    numeric_pipe = Pipeline([("imputer", SimpleImputer(strategy="median")), ("scale", StandardScaler())])
    categorical_pipe = Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))])
    prep = ColumnTransformer([("num", numeric_pipe, NUMERIC_FEATURES), ("cat", categorical_pipe, CATEGORICAL_FEATURES)])
    clf = RandomForestClassifier(n_estimators=trees, random_state=random_state, n_jobs=-1, class_weight="balanced_subsample", min_samples_leaf=2)
    pipe = Pipeline([("preprocess", prep), ("model", clf)])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)
    pipe.fit(X_train, y_train)
    pred = pipe.predict(X_test)
    metrics = {
        "rows_used": len(df), "train_rows": len(X_train), "test_rows": len(X_test),
        "target": target, "accuracy": float(accuracy_score(y_test, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_test, pred)),
        "macro_f1": float(f1_score(y_test, pred, average="macro", zero_division=0)),
        "weighted_f1": float(f1_score(y_test, pred, average="weighted", zero_division=0)),
        "classification_report": classification_report(y_test, pred, output_dict=True, zero_division=0),
        "feature_columns": FEATURE_COLUMNS,
        "source": "ASUSE 2023-24",
    }
    if target == "profitable":
        metrics.update({
            "precision": float(precision_score(y_test, pred, zero_division=0)),
            "recall": float(recall_score(y_test, pred, zero_division=0)),
            "f1": float(f1_score(y_test, pred, zero_division=0)),
            "roc_auc": float(roc_auc_score(y_test, pipe.predict_proba(X_test)[:, 1])),
        })
    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    Path(metrics_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, model_path)
    Path(metrics_path).write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


def cli():
    p = argparse.ArgumentParser(description="Train UdyamSetu's ASUSE profitability model.")
    p.add_argument("--data", default="data/asuse_2023_24_training.csv")
    p.add_argument("--model", default="models/asuse_profitability.joblib")
    p.add_argument("--metrics", default="models/asuse_profitability_metrics.json")
    p.add_argument("--sample-size", type=int, default=None, help="Optional row limit for fast/manual experiments")
    p.add_argument("--test-size", type=float, default=0.2)
    p.add_argument("--trees", type=int, default=200)
    p.add_argument("--target", choices=["profitability_tier", "profitable"], default="profitability_tier")
    args = p.parse_args()
    print(json.dumps(train(args.data, args.model, args.metrics, args.test_size, args.sample_size, trees=args.trees, target=args.target), indent=2))

if __name__ == "__main__":
    cli()
