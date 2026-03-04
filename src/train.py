from __future__ import annotations

import argparse
from pathlib import Path
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

BASE = Path(__file__).resolve().parents[1]
DATA_PATH = BASE / "data" / "collections_synthetic.csv"
MODEL_PATH = BASE / "data" / "repayment_model.joblib"

NUM = [
    "days_past_due",
    "amount_due",
    "paid_on_time_ratio_12m",
    "missed_payments_12m",
    "prev_contacted",
    "prev_response",
]
CAT = ["contact_channel", "risk_segment"]
TARGET = "repaid_30d"
REQUIRED_COLUMNS = NUM + CAT + [TARGET]


def load_and_validate(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return df


def main(input_path: Path) -> None:
    df = load_and_validate(input_path)
    X = df[NUM + CAT]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    pre = ColumnTransformer(
        transformers=[
            ("num", "passthrough", NUM),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CAT),
        ]
    )

    model = Pipeline(
        steps=[
            ("pre", pre),
            ("clf", RandomForestClassifier(n_estimators=300, max_depth=8, random_state=42, class_weight="balanced_subsample")),
        ]
    )

    model.fit(X_train, y_train)
    p = model.predict_proba(X_test)[:, 1]
    y_hat = (p >= 0.5).astype(int)

    print("AUC:", round(roc_auc_score(y_test, p), 4))
    print(classification_report(y_test, y_hat))

    joblib.dump(model, MODEL_PATH)
    print(f"✅ Model saved to: {MODEL_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train repayment model with your own CSV data")
    parser.add_argument("--input", type=Path, default=DATA_PATH, help="Path to input CSV")
    args = parser.parse_args()
    main(args.input)
