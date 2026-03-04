from __future__ import annotations

from pathlib import Path
import pandas as pd
import streamlit as st

BASE = Path(__file__).resolve().parents[1]
PRED_PATH = BASE / "data" / "predictions.csv"

st.set_page_config(page_title="Smart Collections Prioritizer", layout="wide")
st.title("💳 Smart Collections / Risk Prioritizer")
st.caption("MVP: repay probability + strategy + prioritized queue")

if not PRED_PATH.exists():
    st.warning("predictions.csv not found. Run: generate_data.py, train.py, prioritize.py")
    st.stop()

df = pd.read_csv(PRED_PATH)

c1, c2, c3 = st.columns(3)
c1.metric("Accounts", len(df))
c2.metric("Expected recovery (top 20%)", f"${df['sim_expected_recovery_top'].iloc[0]:,.0f}")
c3.metric("Lift vs average", f"{df['sim_lift_vs_average_pct'].iloc[0]:.1f}%")

seg = st.multiselect("Risk segment", sorted(df["risk_segment"].unique()), default=sorted(df["risk_segment"].unique()))
channel = st.multiselect("Preferred channel", sorted(df["contact_channel"].unique()), default=sorted(df["contact_channel"].unique()))

view = df[df["risk_segment"].isin(seg) & df["contact_channel"].isin(channel)].copy()
view = view.sort_values(by=["priority_score", "amount_due"], ascending=[False, False])

st.subheader("Prioritized queue")
st.dataframe(
    view[[
        "account_id",
        "days_past_due",
        "amount_due",
        "risk_segment",
        "repay_probability",
        "priority_score",
        "recommended_strategy",
    ]],
    width="stretch",
)

if st.button("Generate collections action plan"):
    top = view.head(20)
    lines = ["# Weekly Collections Action Plan\n"]
    for _, r in top.iterrows():
        lines.append(
            f"- **{r['account_id']}** | score={r['priority_score']:.2f} | repay={r['repay_probability']:.2f} | due=${r['amount_due']:.0f}\\n"
            f"  - Segment: {r['risk_segment']} / DPD: {int(r['days_past_due'])}\\n"
            f"  - Strategy: {r['recommended_strategy']}"
        )
    report = "\n".join(lines)
    st.markdown(report)
    st.download_button("Download plan (.md)", report, "weekly_collections_plan.md", "text/markdown")
