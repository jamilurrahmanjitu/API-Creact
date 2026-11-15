"""Evaluate without duplicate-row leakage, then fit the deployment model on all data."""
from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import accuracy_score, classification_report

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "heart.csv"
FEATURES = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
            "thalach", "exang", "oldpeak", "slope", "ca", "thal"]

if not DATA.exists():
    raise FileNotFoundError("Place Kaggle's heart.csv at data/heart.csv before training.")
df = pd.read_csv(DATA)
required = FEATURES + ["target"]
missing = set(required) - set(df.columns)
if missing:
    raise ValueError(f"Dataset is missing columns: {sorted(missing)}")
df = df[required].dropna()
X, y = df[FEATURES], df["target"].astype(int)
# Identical feature rows are kept in the same partition to avoid duplicate leakage.
groups = X.astype(str).agg("|".join, axis=1)
splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
train_idx, test_idx = next(splitter.split(X, y, groups=groups))
evaluation_model = RandomForestClassifier(
    n_estimators=200, random_state=42, class_weight="balanced"
)
evaluation_model.fit(X.iloc[train_idx], y.iloc[train_idx])
predictions = evaluation_model.predict(X.iloc[test_idx])
print("Duplicate-group holdout accuracy:", round(accuracy_score(y.iloc[test_idx], predictions), 4))
print(classification_report(y.iloc[test_idx], predictions))

# Refit on all available rows for deployment after the holdout evaluation.
final_model = RandomForestClassifier(
    n_estimators=200, random_state=42, class_weight="balanced"
)
final_model.fit(X, y)
(ROOT / "model").mkdir(exist_ok=True)
joblib.dump(final_model, ROOT / "model" / "heart_model.joblib")
print(f"Trained deployment model on {len(df)} rows; saved model/heart_model.joblib")
