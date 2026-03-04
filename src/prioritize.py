from __future__ import annotations

import argparse
from pathlib import Path
import joblib
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATA_PATH = BASE / "data" / "collections_synthetic.csv"
MODEL_PATH = BASE / "data" / "repayment_model.joblib"
OUT_PATH = BASE / "data" / "predictions.csv"

FEATURES = [
    "days_past_due",
    "amount_due",
    "paid_on_time_ratio_12m",
    "missed_payments_12m",
    "prev_contacted",
    "prev_response",
    "contact_channel",
    "risk_segment",
]


def load_and_validate(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    df = pd.read_csv(path)
    missing = [c for c in FEATURES if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return df


def recommended_strategy(row: pd.Series) -> str:
    if row["days_past_due"] > 75:
        return "call | immediate | firm"
    if row["repay_probability"] >= 0.65:
        return "whatsapp | within 24h | friendly"
    if row["days_past_due"] <= 30:
        return "sms | evening | gentle reminder"
    return "whatsapp | 24-48h | structured payment plan"


def priority_score(row: pd.Series) -> float:
    value_component = min(row["amount_due"] / 1500, 1)
    urgency = min(row["days_past_due"] / 120, 1)
    repay_component = row["repay_probability"]
    score = 0.35 * value_component + 0.15 * urgency + 0.50 * repay_component
    return float(np.clip(score, 0, 1))


def simulate_top_k(df: pd.DataFrame, pct: float = 0.2) -> dict:
    n = max(1, int(len(df) * pct))
    top = df.sort_values("priority_score", ascending=False).head(n)

    expected_recovery = float((top["amount_due"] * top["repay_probability"]).sum())
    avg_prob_top = float(top["repay_probability"].mean())
    avg_prob_all = float(df["repay_probability"].mean())

    return {
        "top_n": n,
        "expected_recovery_top": round(expected_recovery, 2),
        "avg_repay_prob_top": round(avg_prob_top, 4),
        "avg_repay_prob_all": round(avg_prob_all, 4),
        "lift_vs_average": round((avg_prob_top / avg_prob_all - 1) * 100, 2) if avg_prob_all > 0 else None,
    }


def main(input_path: Path) -> None:
    df = load_and_validate(input_path)
    model = joblib.load(MODEL_PATH)

    df["repay_probability"] = model.predict_proba(df[FEATURES])[:, 1]
    df["recommended_strategy"] = df.apply(recommended_strategy, axis=1)
    df["priority_score"] = df.apply(priority_score, axis=1)

    sim = simulate_top_k(df, pct=0.2)
    df["sim_top_n"] = sim["top_n"]
    df["sim_expected_recovery_top"] = sim["expected_recovery_top"]
    df["sim_lift_vs_average_pct"] = sim["lift_vs_average"]

    ranked = df.sort_values(by=["priority_score", "amount_due"], ascending=[False, False])
    ranked.to_csv(OUT_PATH, index=False)

    print(f"✅ Predictions saved to: {OUT_PATH}")
    print("Simulation top 20%:", sim)
    print(ranked[["account_id", "priority_score", "repay_probability", "recommended_strategy"]].head(10).to_string(index=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prioritize collections queue from input CSV")
    parser.add_argument("--input", type=Path, default=DATA_PATH, help="Path to input CSV")
    args = parser.parse_args()
    main(args.input)
