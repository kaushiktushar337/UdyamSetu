# UdyamSetu — ASUSE 2023–24 Trainable ML Pipeline

This version replaces the old World Bank/ISES-specific training assumptions with the **Government of India ASUSE 2023–24 establishment data** supplied to the project.

## What is trained

The pipeline creates one establishment-level record by joining the ASUSE blocks using:

`FSU serial + sample establishment + second-stage stratum + segment`

The supervised target used by default is:

- `profitability_tier = low / medium / high`
- tiers are the lower, middle and upper thirds of observed **net surplus (Block 14, item 1402)**.

A binary `profitable = net_surplus > 0` target is also retained, but it is extremely imbalanced in this extract and is **not the default target**.

The model is a lightweight scikit-learn Random Forest with preprocessing for numeric and categorical variables.

## Build the training data manually

From the project root:

```bash
python -m ml_engine.training.asuse_pipeline /path/to/ASUSE_DATA_2023_24_CSV.zip \
  --output data/asuse_2023_24_training.csv
```

The raw archive is not modified.

## Train manually

Fast experiment:

```bash
python -m ml_engine.training.train_asuse_model \
  --data data/asuse_2023_24_training.csv \
  --model models/asuse_profitability.joblib \
  --metrics models/asuse_profitability_metrics.json \
  --sample-size 20000 \
  --trees 50
```

Larger training run:

```bash
python -m ml_engine.training.train_asuse_model \
  --data data/asuse_2023_24_training.csv \
  --model models/asuse_profitability.joblib \
  --metrics models/asuse_profitability_metrics.json \
  --trees 250
```

Choose the legacy binary target explicitly if required:

```bash
python -m ml_engine.training.train_asuse_model --target profitable
```

## Test manually

```bash
python -m ml_engine.training.test_asuse_model \
  --data data/asuse_2023_24_training.csv \
  --model models/asuse_profitability.joblib
```

The training command also performs a stratified train/test split and writes evaluation metrics to the JSON file.

## Features

The model uses establishment characteristics available before the target outcome, including:

- sector, district and urban/rural location
- NIC activity codes
- ownership and establishment type
- education and technical training
- years/months operated and daily work hours
- bank account, accounting, computer and internet usage
- registration and business-operation indicators
- total workers
- owned/hired fixed assets
- net additions to fixed assets

Revenue/expense components used to calculate net surplus are deliberately not used as model features, reducing direct target leakage.

## Current tested result

A 20,000-row manual training run with 50 trees completed successfully:

- Train: 16,000
- Test: 4,000
- Accuracy: **67.4%**
- Balanced accuracy: **67.36%**
- Macro F1: **67.52%**

This is a baseline, not a final production model. The full 363,520-establishment derived training frame is available after preprocessing and can be trained with a larger forest when compute/time permits.

## Important limitation

ASUSE is a cross-sectional survey. The model learns associations between establishment characteristics and observed net-surplus tiers; it should therefore be treated as a **decision-support signal**, not as a guaranteed forecast of future business success.
