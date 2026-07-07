# Daily Reconciliation Breaks Review

Simulated investment operations reconciliation dashboard for reviewing trade, position, and cash breaks across internal and custodian records.

## Running the dashboard

1. Generate exception data: `python src/reconciliation.py`
2. Launch the dashboard: `streamlit run app.py`

## Scope and limitations

The project intentionally uses a small simulated dataset to make the reconciliation logic easy to review. Future improvements include larger data coverage, SQL integration, exception aging history, and automated email alerts.
