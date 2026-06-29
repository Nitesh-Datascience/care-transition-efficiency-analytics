# Care Transition Efficiency & Placement Outcome Analytics

This submission converts the HHS Unaccompanied Alien Children Program dataset into a process-efficiency and placement-outcome analytics project.

## Contents
- `app.py` - Streamlit dashboard with date filters, KPI toggles, threshold alerts, and bottleneck views.
- `data/processed_care_transition_metrics.csv` - cleaned dataset with derived KPIs.
- `data/monthly_kpi_summary.csv`, `data/weekday_pattern_summary.csv`, `data/top_bottleneck_periods.csv` - summary outputs.
- `charts/` - static visualizations used in the reports.
- `research_paper_care_transition.docx` and `.pdf` - detailed EDA, methodology, insights, and recommendations.
- `executive_summary_care_transition.docx` and `.pdf` - stakeholder-ready summary.
- `requirements.txt` - packages needed to run the dashboard.

## Run the dashboard
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Dataset coverage
Cleaned valid reporting records: 720 rows, from 2023-01-12 to 2025-12-21.

## Core KPI formulas
- Transfer Efficiency Ratio = Children transferred out of CBP custody / Children in CBP custody
- Discharge Effectiveness Index = Children discharged from HHS Care / Children in HHS Care
- Pipeline Throughput = Children discharged from HHS Care / Children apprehended and placed in CBP custody
- Backlog Accumulation Rate = Transfers to HHS - Discharges from HHS
- Outcome Stability Score = inverse coefficient of variation of discharge effectiveness over a rolling 30-day window
