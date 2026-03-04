# Smart Collections / Risk Prioritizer (Mini-Agent #2)

An MVP for fintech collections/risk operations to prioritize actions and maximize recovery with constrained operational capacity.

## Value proposition

With the same ops team, this agent helps you:
- prioritize who to contact first,
- choose the best channel/timing/tone,
- estimate expected impact when targeting the top 20% queue.

## Input

- days past due
- payment history
- amount due
- preferred contact channel
- previous interaction outcome (contacted/not contacted, responded)

## Output

- `repay_probability`
- `recommended_strategy` (channel + timing + tone)
- `priority_score`
- prioritized queue for collections/risk ops
- expected recovery simulator

## Project structure

```bash
mini-agent-fintech-collections/
├─ data/
│  ├─ collections_synthetic.csv
│  ├─ predictions.csv
│  └─ repayment_model.joblib
├─ src/
│  ├─ generate_data.py
│  ├─ train.py
│  ├─ prioritize.py
│  └─ app.py
├─ notebooks/
│  └─ mvp_walkthrough.ipynb
├─ requirements.txt
└─ README.md
```

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python src/generate_data.py
python src/train.py
python src/prioritize.py
streamlit run src/app.py
```

## Bring your own data (BYOD)

1. Copy the template:
   - `cp data/input_template.csv data/collections.csv`
2. Fill `data/collections.csv` with your own records, keeping the same column names.
3. (Recommended) Run a data quality check first:
   - `python src/data_quality.py --input data/collections.csv`
4. Train and prioritize with your file:
   - `python src/train.py --input data/collections.csv`
   - `python src/prioritize.py --input data/collections.csv`

## 60-second demo script

- 0–10s: “Built for fintech collections to improve recovery KPI.”
- 10–25s: “Inputs: DPD, amount, payment history, contact interaction.”
- 25–40s: “Model outputs repay probability + strategy + prioritized queue.”
- 40–55s: “Simulator estimates lift if the team contacts the top-priority segment first.”
- 55–60s: “Can adapt to your stack in 1–2 weeks.”
