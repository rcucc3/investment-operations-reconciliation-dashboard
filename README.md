# Daily Reconciliation Breaks Review

Python project that simulates an investment operations reconciliation workflow
It compares internal books to custodian records, flag breaks, estimate exposure, and prioritize what an ops analyst should review first.
I built this project to better understand how investment operations teams review breaks between internal records and custodian data. The focus was on comparing data across systems, identifying exceptions, prioritizing issues by risk and estimated exposure, and creating reports that an operations analyst could use for daily review.


**Stack:** Python · pandas · Streamlit · Plotly · openpyxl

## Highlights
- Reconciles trades, holdings, and cash between internal and custodian files
- Flags missing records, quantity/price mismatches, settlement-date differences, and account/currency breaks
- Assigns risk, priority, owner, aging, and likely root cause with transparent rule-based logic
- Estimates dollar exposure so high-impact breaks surface first
- Produces a formatted Excel exception workbook and an interactive Streamlit review dashboard
- Uses a reproducible simulated dataset with deliberately injected breaks for validation

## Why I built it
I built this to practice the kind of work that shows up in investment operations, including reconciliation, exception review, risk prioritization, and control reporting.
The working question behind it:
> How does an operations analyst quickly find mismatches between two systems and decide what to escalate first?
The project is structured around that daily review workflow, not just chart generation.

## How the reconciliation works
The engine compares internal and custodian files side by side and flags mismatches across three workflows.

### Trade breaks
Missing on either side · quantity / price differences · settlement date mismatches · currency and buy/sell direction issues

### Position breaks
Missing holdings · quantity / market-price differences · currency and custodian-account mismatches

### Cash breaks
Balance differences · missing cash records · reporting-date and custodian-account mismatches

Each exception lands in a standardized report with portfolio, security, break type, internal vs custodian values, estimated exposure, risk/priority, owner, days open, root cause, recommended action, and status.

## Dashboard
Streamlit app designed as a **daily breaks review** (not a generic BI page):
- Breaks overview metrics
- Items requiring first review (Critical / High, ranked by exposure and age)
- Open breaks by workflow, risk mix, estimated exposure by portfolio, likely root cause
- Full priority queue plus filters
- CSV and Excel downloads

## Excel output
`Investment_Operations_Exception_Report.xlsx` includes summary, all/trade/position/cash exceptions, high-risk items, and portfolio / workflow / root-cause tabs — with filters, frozen headers, currency formatting, and conditional formatting.

## Sample data
`generate_sample_data.py` builds a fixed-seed demo set (about 50 trades, 25 positions, 5 cash accounts per side, with 18 injected exceptions). The small scope is intentional so the matching logic and exception rules are easy to inspect.


## Run it
```bash
python -m pip install -r requirements.txt
python src/generate_sample_data.py
python src/reconciliation.py
python -m streamlit run app.py
```


## Project structure

```text
├── data/
│   ├── cash_custodian.csv
│   ├── cash_internal.csv
│   ├── holdings_custodian.csv
│   ├── holdings_internal.csv
│   ├── trades_custodian.csv
│   ├── trades_internal.csv
│   └── generated/                 # expanded sample set + injected breaks
│       ├── trades_*_generated.csv
│       ├── holdings_*_generated.csv
│       ├── cash_*_generated.csv
│       └── injected_*_exceptions.csv
├── output/
│   ├── all_exceptions.csv
│   ├── trade_exceptions.csv
│   ├── position_exceptions.csv
│   ├── cash_exceptions.csv
│   └── Investment_Operations_Exception_Report.xlsx
├── screenshots/
│   ├── dashboard_overview.png
│   ├── dashboard_workflow_risk.png
│   ├── dashboard_exposure_root_cause.png
│   ├── dashboard_priority_queue.png
│   └── dashboard_break_review_filters.png
├── src/
│   ├── generate_sample_data.py
│   └── reconciliation.py
├── app.py                         # Streamlit dashboard
├── requirements.txt
├── .gitignore
└── README.md
```

## Limitations

This is a simulation. Production reconciliation would likely involve larger datasets, SQL storage, stronger security identifiers, historical aging, audit trails, permissions, automated ingestion, and formal escalation paths.

Risk, priority, ownership, and root cause are assigned using demonstration rules, not live control settings.

## What I would add next

- SQL-backed storage and exception history
- Status updates / resolution timestamps in the UI
- Automated alerts for aged or critical breaks
- Unit tests around matching and classification rules