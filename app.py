from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATA_PATH = Path(__file__).parent / "data" / "BTCUSDT_simulation_results.csv"


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)

    numeric_cols = [
        "balance",
        "minBalance",
        "maxBalance",
        "winNumber",
        "errorNumber",
        "maxPosition",
        "tpDiversionX100",
        "slDiversionMultiplayer100",
        "wagerMultiplayer",
        "leverage",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["totalTrades"] = df["winNumber"].fillna(0) + df["errorNumber"].fillna(0)
    df["winRate"] = (df["winNumber"] / df["totalTrades"].replace(0, pd.NA)) * 100
    df["balanceRange"] = df["maxBalance"] - df["minBalance"]
    df["endMonthLabel"] = df["endMonth"].astype(str)
    return df


def format_currency(value: float) -> str:
    return f"${value:,.0f}"


st.set_page_config(page_title="Trading Performance Analytics", page_icon="📊", layout="wide")
st.title("Trading Performance Analytics Dashboard")
st.caption("Interactive analysis of trading-simulation performance, risk exposure and strategy settings.")

try:
    data = load_data()
except FileNotFoundError:
    st.error(f"Dataset not found: {DATA_PATH}")
    st.stop()

st.sidebar.header("Filters")

available_months = sorted(data["endMonthLabel"].dropna().unique().tolist())
selected_months = st.sidebar.multiselect("Simulation end month", available_months, default=available_months)

available_tp = sorted(data["tpDiversionX100"].dropna().unique().tolist())
selected_tp = st.sidebar.multiselect("Take-profit setting", available_tp, default=available_tp)

available_sl = sorted(data["slDiversionMultiplayer100"].dropna().unique().tolist())
selected_sl = st.sidebar.multiselect("Stop-loss setting", available_sl, default=available_sl)

filtered = data[
    data["endMonthLabel"].isin(selected_months)
    & data["tpDiversionX100"].isin(selected_tp)
    & data["slDiversionMultiplayer100"].isin(selected_sl)
].copy()

if filtered.empty:
    st.warning("No simulation runs match the selected filters.")
    st.stop()

wins = filtered["winNumber"].sum()
losses = filtered["errorNumber"].sum()
win_rate = wins / (wins + losses) * 100 if (wins + losses) else 0

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Simulation runs", f"{len(filtered):,}")
kpi2.metric("Overall win rate", f"{win_rate:.1f}%")
kpi3.metric("Average final balance", format_currency(filtered["balance"].mean()))
kpi4.metric("Best final balance", format_currency(filtered["balance"].max()))

st.subheader("Performance over time")
monthly = (
    filtered.groupby("endMonthLabel", as_index=False)
    .agg(
        average_balance=("balance", "mean"),
        wins=("winNumber", "sum"),
        losses=("errorNumber", "sum"),
    )
    .sort_values("endMonthLabel")
)
monthly["win_rate"] = monthly["wins"] / (monthly["wins"] + monthly["losses"]) * 100

fig_balance = px.line(
    monthly,
    x="endMonthLabel",
    y="average_balance",
    markers=True,
    labels={"endMonthLabel": "End month", "average_balance": "Average final balance"},
)
st.plotly_chart(fig_balance, use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("Win rate by period")
    fig_win = px.bar(
        monthly,
        x="endMonthLabel",
        y="win_rate",
        labels={"endMonthLabel": "End month", "win_rate": "Win rate (%)"},
    )
    st.plotly_chart(fig_win, use_container_width=True)

with right:
    st.subheader("Risk vs. outcome")
    fig_risk = px.scatter(
        filtered,
        x="maxPosition",
        y="balance",
        size="totalTrades",
        hover_data=["endMonthLabel", "winRate", "tpDiversionX100", "slDiversionMultiplayer100"],
        labels={"maxPosition": "Maximum position", "balance": "Final balance"},
    )
    st.plotly_chart(fig_risk, use_container_width=True)

st.subheader("Top simulation configurations")
columns = [
    "id",
    "symbol",
    "startMonth",
    "endMonth",
    "tpDiversionX100",
    "slDiversionMultiplayer100",
    "balance",
    "winRate",
    "maxPosition",
]
st.dataframe(
    filtered.sort_values("balance", ascending=False)[columns].head(20),
    use_container_width=True,
    hide_index=True,
)

with st.expander("About the metrics"):
    st.markdown(
        """
- **Overall win rate** = wins / (wins + losses).
- **Average final balance** compares ending account balance across selected simulation runs.
- **Maximum position** is used as a simple risk/exposure proxy.
- The included dataset is a historical simulation sample for reproducibility.
        """
    )
