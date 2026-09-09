# ASUSE training data

The training CSV in this directory is the prepared ASUSE 2023–24 dataset used by the manual training pipeline.

Train the model from the `backend` directory with:

```powershell
python -m ml_engine.training.train_asuse_model --data data/asuse_2023_24_training.csv --model models/asuse_profitability.joblib
```

The dataset is a large file. GitHub accepts files below 100 MB but warns above 50 MB. Git LFS is recommended if the repository will be used for ongoing model-training work.
