# Heart Disease Prediction API

A small FastAPI + scikit-learn + Docker project for the assignment. The API accepts 13 features and returns a binary classifier prediction.

> **Important:** Educational software only. It is not a medical device, diagnosis, screening tool, or substitute for a qualified clinician. Do not use its output for healthcare decisions.

## Project layout

```text
heart-disease-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── schemas.py
├── model/
│   └── heart_model.joblib
├── data/                 # put Kaggle heart.csv here (not committed)
├── train_model.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 1. Get the dataset and train

Download `heart.csv` from [Kaggle: Heart Disease Dataset](https://www.kaggle.com/datasets/johnsmith88/heart-disease-dataset), then place it at `data/heart.csv`. Expected columns are the 13 API features plus `target` (0 = absence, 1 = presence).

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
python train_model.py
```

The training script evaluates a Random Forest using an 80/20 holdout split that keeps identical feature rows together (to reduce duplicate-row leakage), prints the classification report, then refits the deployment model on all available rows. It creates `model/heart_model.joblib`.

For the supplied 1,025-row CSV, the duplicate-group holdout accuracy was **0.7714 (77.14%)**. This is a simple internal evaluation on this dataset, not an estimate of real-world clinical performance.

## 2. Run locally without Docker

```bash
uvicorn app.main:app --reload
```

Open http://localhost:8000/docs.

## 3. Docker

```bash
docker compose build
docker compose up
```

Open http://localhost:8000/docs. Stop with `Ctrl+C` (or `docker compose down`).

## 4. API

- `GET /health` — process and model status
- `GET /info` — classifier type and feature order
- `POST /predict` — binary prediction and (when supported) positive-class probability

Example request:

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age": 52, "sex": 1, "cp": 0, "trestbps": 125,
    "chol": 212, "fbs": 0, "restecg": 1, "thalach": 168,
    "exang": 0, "oldpeak": 1.0, "slope": 2, "ca": 2, "thal": 3
  }'
```

Example response:

```json
{"heart_disease": false, "probability": 0.12}
```

The probability shown above is illustrative; actual output depends on the trained model.

## 5. Deploy to Render

1. Push this project to a GitHub repository.
2. In Render, choose **New + → Web Service** and connect the repository.
3. Set **Language/Environment: Docker** and the root directory/build context to the repository root.
4. Deploy. The Dockerfile binds Uvicorn to `0.0.0.0` and uses Render's `$PORT`.
5. Test `https://YOUR-SERVICE.onrender.com/health`, `/info`, and `/docs`.

No separate start command is required because it is defined in the Dockerfile.

## 6. GitHub submission

Create a new GitHub repository, then from this folder run:

```bash
git init
git add .
git commit -m "Build heart disease prediction API with Docker"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

Submit the GitHub repository URL and the live Render URL after deployment. Those accounts/deployments must be created by you; this project archive does not publish to GitHub or Render automatically.

## Dataset note

The supplied CSV contains 1,025 rows, 13 predictor columns plus `target`, and no missing values in those columns. It contains repeated records; the evaluation split groups identical predictor rows together to reduce train/test leakage. The raw CSV is excluded from Git by `.gitignore`; keep it locally at `data/heart.csv` if you need to retrain. Model metrics are for demonstration and do not establish clinical validity.
