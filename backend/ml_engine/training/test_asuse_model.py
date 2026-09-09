from __future__ import annotations
import argparse, json, joblib
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, classification_report
from .asuse_pipeline import FEATURE_COLUMNS, load_training_frame

def evaluate(data_path, model_path, target="profitability_tier", sample_size=None, random_state=123):
    df = load_training_frame(data_path)
    if sample_size and sample_size < len(df): df = df.sample(sample_size, random_state=random_state)
    model = joblib.load(model_path)
    pred = model.predict(df[FEATURE_COLUMNS]); y = df[target]
    return {"rows_tested": len(df), "target": target, "accuracy": float(accuracy_score(y,pred)), "balanced_accuracy": float(balanced_accuracy_score(y,pred)), "macro_f1": float(f1_score(y,pred,average="macro",zero_division=0)), "weighted_f1": float(f1_score(y,pred,average="weighted",zero_division=0)), "classification_report": classification_report(y,pred,output_dict=True,zero_division=0)}

def cli():
    p=argparse.ArgumentParser(description="Evaluate a trained UdyamSetu ASUSE model.")
    p.add_argument("--data",default="data/asuse_2023_24_training.csv"); p.add_argument("--model",default="models/asuse_profitability.joblib"); p.add_argument("--target",choices=["profitability_tier","profitable"],default="profitability_tier"); p.add_argument("--sample-size",type=int,default=None)
    a=p.parse_args(); print(json.dumps(evaluate(a.data,a.model,a.target,a.sample_size),indent=2))
if __name__ == "__main__": cli()
