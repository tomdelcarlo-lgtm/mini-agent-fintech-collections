# Data Quality Report (Fintech Collections Prioritizer)

- Input file: `data/collections_synthetic.csv`
- Rows: 1200
- Overall status: **PASS**

## Schema checks
- Missing required columns: None
- Duplicate account_id: 0

## Null checks
- account_id: 0 null(s) (0.00%)
- days_past_due: 0 null(s) (0.00%)
- amount_due: 0 null(s) (0.00%)
- paid_on_time_ratio_12m: 0 null(s) (0.00%)
- missed_payments_12m: 0 null(s) (0.00%)
- contact_channel: 0 null(s) (0.00%)
- prev_contacted: 0 null(s) (0.00%)
- prev_response: 0 null(s) (0.00%)
- risk_segment: 0 null(s) (0.00%)

## Category checks
- Categorical fields look valid

## Range checks
- All numeric ranges look valid