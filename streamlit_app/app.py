from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[1]
GOLD_PATH = REPO_ROOT / "data" / "curated" / "gold" / "gold_provider_monthly_staffing_metrics" / "part-00000.parquet"
st.set_page_config(page_title="Healthcare Staffing Metrics", layout="wide")
st.title("Healthcare Staffing Metrics Dashboard")
st.caption("Dashboard-ready metrics from the curated gold table.")

@st.cache_data
def load_data() -> pd.DataFrame:
    if not GOLD_PATH.exists():
        st.error(f"Gold metrics file not found: {GOLD_PATH}")
        st.stop()
    return pd.read_parquet(GOLD_PATH)

df = load_data()
st.sidebar.header("Filters")
states = sorted([s for s in df["state"].dropna().unique() if str(s).strip()]) if "state" in df.columns else []
selected_states = st.sidebar.multiselect("State", states, default=states[:10] if len(states) > 10 else states)
filtered = df.copy()
if selected_states:
    filtered = filtered[filtered["state"].isin(selected_states)]
provider_search = st.sidebar.text_input("Provider name contains")
if provider_search and "provider_name" in filtered.columns:
    filtered = filtered[filtered["provider_name"].fillna("").str.contains(provider_search, case=False, na=False)]

st.subheader("Summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Providers", f"{filtered['provider_id'].nunique():,}")
col2.metric("Avg nurse HPRD", f"{filtered['avg_total_nurse_hours_per_resident_day'].mean():.2f}")
col3.metric("Avg RN HPRD", f"{filtered['avg_rn_hours_per_resident_day'].mean():.2f}")
col4.metric("Avg bed utilization", f"{filtered['bed_utilization_rate'].mean():.1%}")

st.subheader("Staffing Trend by Month")
monthly = filtered.groupby("year_month", as_index=False).agg(
    avg_total_nurse_hours_per_resident_day=("avg_total_nurse_hours_per_resident_day", "mean"),
    avg_rn_hours_per_resident_day=("avg_rn_hours_per_resident_day", "mean"),
    avg_contract_staff_ratio=("avg_contract_staff_ratio", "mean"),
    bed_utilization_rate=("bed_utilization_rate", "mean"),
).sort_values("year_month")
if not monthly.empty:
    fig = px.line(monthly, x="year_month", y="avg_total_nurse_hours_per_resident_day", markers=True, title="Average Total Nurse Hours per Resident Day by Month")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Average Staffing by State")
state_summary = filtered.groupby("state", as_index=False).agg(
    providers=("provider_id", "nunique"),
    avg_total_nurse_hours_per_resident_day=("avg_total_nurse_hours_per_resident_day", "mean"),
    avg_rn_hours_per_resident_day=("avg_rn_hours_per_resident_day", "mean"),
    avg_contract_staff_ratio=("avg_contract_staff_ratio", "mean"),
    bed_utilization_rate=("bed_utilization_rate", "mean"),
).dropna(subset=["state"]).sort_values("avg_total_nurse_hours_per_resident_day", ascending=False)
if not state_summary.empty:
    fig = px.bar(state_summary, x="state", y="avg_total_nurse_hours_per_resident_day", title="Average Total Nurse Hours per Resident Day by State")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Facilities with Low Staffing Compared to Resident Load")
low_staffing = filtered.dropna(subset=["avg_total_nurse_hours_per_resident_day"]).sort_values("avg_total_nurse_hours_per_resident_day").loc[:, [
    "provider_id", "provider_name", "state", "year_month", "avg_daily_census", "avg_total_nurse_hours_per_resident_day", "avg_rn_hours_per_resident_day", "bed_utilization_rate"
]].head(25)
st.dataframe(low_staffing, use_container_width=True)

st.subheader("Contract Staff Ratio")
contract_view = filtered.dropna(subset=["avg_contract_staff_ratio"]).sort_values("avg_contract_staff_ratio", ascending=False).head(25)
st.dataframe(contract_view[["provider_id", "provider_name", "state", "year_month", "avg_contract_staff_ratio", "total_contract_nurse_hours", "total_nurse_hours"]], use_container_width=True)

st.subheader("Gold Table Preview")
st.dataframe(filtered.head(100), use_container_width=True)
