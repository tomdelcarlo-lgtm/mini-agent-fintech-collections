from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = BASE / "data" / "collections_synthetic.csv"
DEFAULT_OUT = BASE / "data" / "data_quality_report.md"

REQUIRED_COLUMNS = [
    "account_id",
    "days_past_due",
    "amount_due",
    "paid_on_time_ratio_12m",
    "missed_payments_12m",
    "contact_channel",
    "prev_contacted",
    "prev_response",
    "risk_segment",
]

ALLOWED_CHANNELS = {"whatsapp", "sms", "email", "call"}
ALLOWED_SEGMENTS = {"early", "mid", "late", "severe"}
RANGES = {
    "days_past_due": (0, 365),
    "amount_due": (0, None),
    "paid_on_time_ratio_12m": (0, 1),
    "missed_payments_12m": (0, None),
    "prev_contacted": (0, 1),
    "prev_response": (0, 1),
}


def check_ranges(df: pd.DataFrame) -> list[str]:
    issues: list[str] = []
    for col, (lo, hi) in RANGES.items():
        if col not in df.columns:
            continue
        s = pd.to_numeric(df[col], errors="coerce")
        bad = pd.Series(False, index=df.index)
        if lo is not None:
            bad |= s < lo
        if hi is not None:
            bad |= s > hi
        n_bad = int(bad.sum())
        if n_bad > 0:
            issues.append(f"- {col}: {n_bad} value(s) outside expected range [{lo}, {hi}]")
    return issues


def main(input_path: Path, out_path: Path) -> None:
    df = pd.read_csv(input_path)
    total = len(df)

    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    duplicate_ids = int(df["account_id"].duplicated().sum()) if "account_id" in df.columns else None

    null_lines = []
    for col in REQUIRED_COLUMNS:
        if col in df.columns:
            n_null = int(df[col].isna().sum())
            pct = (n_null / total * 100) if total else 0
            null_lines.append(f"- {col}: {n_null} null(s) ({pct:.2f}%)")

    cat_issues = []
    if "contact_channel" in df.columns:
        invalid = sorted(set(df["contact_channel"].dropna().astype(str).unique()) - ALLOWED_CHANNELS)
        if invalid:
            cat_issues.append(f"- contact_channel: invalid categories found {invalid}")
    if "risk_segment" in df.columns:
        invalid = sorted(set(df["risk_segment"].dropna().astype(str).unique()) - ALLOWED_SEGMENTS)
        if invalid:
            cat_issues.append(f"- risk_segment: invalid categories found {invalid}")

    range_issues = check_ranges(df)

    status = "PASS" if not missing_cols and not cat_issues and not range_issues else "WARN"

    lines = [
        "# Data Quality Report (Fintech Collections Prioritizer)",
        "",
        f"- Input file: `{input_path}`",
        f"- Rows: {total}",
        f"- Overall status: **{status}**",
        "",
        "## Schema checks",
        f"- Missing required columns: {missing_cols if missing_cols else 'None'}",
        f"- Duplicate account_id: {duplicate_ids if duplicate_ids is not None else 'N/A'}",
        "",
        "## Null checks",
        *null_lines,
        "",
        "## Category checks",
        *(cat_issues if cat_issues else ["- Categorical fields look valid"]),
        "",
        "## Range checks",
        *(range_issues if range_issues else ["- All numeric ranges look valid"]),
    ]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Data quality report saved to: {out_path}")
    print(f"Status: {status}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Fintech input data quality report")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path to input CSV")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Path to output markdown report")
    args = parser.parse_args()
    main(args.input, args.out)
