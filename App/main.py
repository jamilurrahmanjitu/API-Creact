from pathlib import Path
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from app.schemas import HeartFeatures

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "model" / "heart_model.joblib"
FEATURES = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
            "thalach", "exang", "oldpeak", "slope", "ca", "thal"]

app = FastAPI(title="Heart Disease Prediction API", version="1.0.0",
              description="Educational demo only. Not for medical diagnosis.")
model = joblib.load(MODEL_PATH)

@app.get("/health")
def health():
    return {"status": "healthy", "model_loaded": model is not None}

@app.get("/info")
def info():
    return {"model_type": type(model).__name__, "features": FEATURES,
            "target": {"0": "absence", "1": "presence"}}

@app.post("/predict")
def predict(payload: HeartFeatures):
    try:
        row = pd.DataFrame([[getattr(payload, f) for f in FEATURES]], columns=FEATURES)
        prediction = int(model.predict(row)[0])
        result = {"heart_disease": bool(prediction)}
        if hasattr(model, "predict_proba"):
            result["probability"] = round(float(model.predict_proba(row)[0][1]), 4)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}")
