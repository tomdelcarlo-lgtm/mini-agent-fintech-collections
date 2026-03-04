from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[1] / "data" / "collections_synthetic.csv"


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-x))


def main(n: int = 1200, seed: int = 7) -> None:
    rng = np.random.default_rng(seed)

    account_id = [f"CUST-{i:05d}" for i in range(1, n + 1)]
    dpd = rng.integers(1, 121, size=n)  # days past due
    amount_due = rng.normal(480, 320, size=n).clip(20, 5000)

    paid_on_time_ratio_12m = rng.normal(0.72, 0.2, size=n).clip(0, 1)
    missed_payments_12m = rng.poisson(2.1, size=n)

    contact_channel = rng.choice(["whatsapp", "sms", "email", "call"], size=n, p=[0.38, 0.22, 0.24, 0.16])
    prev_contacted = rng.binomial(1, 0.55, size=n)
    prev_response = np.where(prev_contacted == 1, rng.binomial(1, 0.42, size=n), 0)

    risk_segment = np.select(
        [dpd <= 15, (dpd > 15) & (dpd <= 45), (dpd > 45) & (dpd <= 75), dpd > 75],
        ["early", "mid", "late", "severe"],
        default="mid",
    )

    channel_weight = np.select(
        [contact_channel == "whatsapp", contact_channel == "sms", contact_channel == "email", contact_channel == "call"],
        [0.2, 0.08, 0.03, -0.04],
    )

    repay_logit = (
        -0.024 * dpd
        -0.0011 * amount_due
        + 1.7 * paid_on_time_ratio_12m
        - 0.23 * missed_payments_12m
        + 0.45 * prev_response
        + 0.12 * prev_contacted
        + channel_weight
        + 0.25
    )

    repay_prob = sigmoid(repay_logit)
    repaid_30d = rng.binomial(1, repay_prob)

    df = pd.DataFrame(
        {
            "account_id": account_id,
            "days_past_due": dpd,
            "amount_due": amount_due.round(2),
            "paid_on_time_ratio_12m": paid_on_time_ratio_12m.round(3),
            "missed_payments_12m": missed_payments_12m,
            "contact_channel": contact_channel,
            "prev_contacted": prev_contacted,
            "prev_response": prev_response,
            "risk_segment": risk_segment,
            "repaid_30d": repaid_30d,
        }
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"✅ Synthetic dataset saved to: {OUT}")
    print(df.head(3).to_string(index=False))


if __name__ == "__main__":
    main()
