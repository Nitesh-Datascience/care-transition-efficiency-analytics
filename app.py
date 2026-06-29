import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Care Transition Analytics", layout="wide")
st.title("Care Transition Efficiency & Placement Outcome Analytics")
st.caption("CBP custody -> HHS care -> sponsor placement process analytics")

DATA_PATH = Path(__file__).parent / "data" / "processed_care_transition_metrics.csv"
df = pd.read_csv(DATA_PATH, parse_dates=["Date"])

with st.sidebar:
    st.header("Controls")
    min_date, max_date = df["Date"].min().date(), df["Date"].max().date()
    date_range = st.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    else:
        start, end = df["Date"].min(), df["Date"].max()
    metric_choice = st.multiselect(
        "Ratio-based metric toggles",
        ["transfer_efficiency_ratio", "discharge_effectiveness_index", "pipeline_throughput", "outcome_stability_score"],
        default=["transfer_efficiency_ratio", "discharge_effectiveness_index"]
    )
    transfer_threshold = st.slider("Transfer efficiency alert threshold", 0.0, 2.0, 0.50, 0.05)
    discharge_threshold = st.slider("Discharge effectiveness alert threshold", 0.0, 0.10, 0.01, 0.001)
    backlog_threshold = st.slider("14-day backlog alert threshold", -1000, 1500, 0, 50)

f = df[(df["Date"] >= start) & (df["Date"] <= end)].copy()
f["transfer_alert"] = f["transfer_efficiency_ratio"] < transfer_threshold
f["discharge_alert"] = f["discharge_effectiveness_index"] < discharge_threshold
f["backlog_alert"] = f["rolling_14d_backlog"] > backlog_threshold

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Apprehended", f"{f['cbp_apprehended'].sum():,.0f}")
c2.metric("Total Transfers", f"{f['cbp_transferred'].sum():,.0f}")
c3.metric("Total Discharges", f"{f['hhs_discharged'].sum():,.0f}")
c4.metric("Net HHS Backlog", f"{f['net_hhs_backlog'].sum():,.0f}")
c5.metric("Avg Stability", f"{f['outcome_stability_score'].mean():.1f}")

st.subheader("Care Pipeline Flow Visualization")
flow_long = f.melt(id_vars="Date", value_vars=["cbp_custody", "hhs_care"], var_name="Stage", value_name="Children")
st.plotly_chart(px.line(flow_long, x="Date", y="Children", color="Stage", title="Active Care Load by Stage"), use_container_width=True)

st.subheader("Transfer & Discharge Efficiency Panels")
if metric_choice:
    metric_long = f.melt(id_vars="Date", value_vars=metric_choice, var_name="Metric", value_name="Value")
    st.plotly_chart(px.line(metric_long, x="Date", y="Value", color="Metric", title="Selected KPI Ratios"), use_container_width=True)
else:
    st.info("Select at least one ratio metric in the sidebar.")

st.subheader("Bottleneck Detection")
b1, b2 = st.columns(2)
with b1:
    st.plotly_chart(px.bar(f, x="Date", y="net_hhs_backlog", title="Daily Net HHS Backlog: Transfers - Discharges"), use_container_width=True)
with b2:
    st.plotly_chart(px.line(f, x="Date", y="rolling_14d_backlog", title="Rolling 14-Day Backlog Accumulation"), use_container_width=True)

alerts = f[f[["transfer_alert", "discharge_alert", "backlog_alert"]].any(axis=1)][["Date", "transfer_efficiency_ratio", "discharge_effectiveness_index", "rolling_14d_backlog", "transfer_alert", "discharge_alert", "backlog_alert"]]
st.warning(f"Alert rows in selected period: {len(alerts):,}")
st.dataframe(alerts.sort_values("Date", ascending=False), use_container_width=True)

st.subheader("Outcome Trend Analysis")
f["month"] = f["Date"].dt.to_period("M").astype(str)
monthly = f.groupby("month", as_index=False).agg(
    apprehended=("cbp_apprehended", "sum"),
    transferred=("cbp_transferred", "sum"),
    discharged=("hhs_discharged", "sum"),
    net_hhs_backlog=("net_hhs_backlog", "sum"),
    avg_transfer_eff=("transfer_efficiency_ratio", "mean"),
    avg_discharge_eff=("discharge_effectiveness_index", "mean"),
    avg_stability=("outcome_stability_score", "mean"),
)
st.plotly_chart(px.bar(monthly, x="month", y=["transferred", "discharged"], barmode="group", title="Monthly Transfers vs Discharges"), use_container_width=True)
st.dataframe(monthly, use_container_width=True)

st.subheader("Raw Metrics")
st.dataframe(f.sort_values("Date", ascending=False), use_container_width=True)
