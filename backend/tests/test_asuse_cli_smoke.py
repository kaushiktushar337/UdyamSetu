from pathlib import Path
import subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "asuse_2023_24_training.csv"
MODEL = ROOT / "models" / "smoke_model.joblib"
METRICS = ROOT / "models" / "smoke_metrics.json"


def test_training_cli_smoke():
    r = subprocess.run([
        sys.executable, "-m", "ml_engine.training.train_asuse_model",
        "--data", str(DATA), "--model", str(MODEL), "--metrics", str(METRICS),
        "--sample-size", "3000", "--trees", "20"
    ], cwd=ROOT, capture_output=True, text=True, timeout=180)
    assert r.returncode == 0, r.stderr
    assert MODEL.exists() and METRICS.exists()
    MODEL.unlink(); METRICS.unlink()
