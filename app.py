"""
Global Superstore Sales Monitor
A small Streamlit dashboard for one decision-maker: the regional sales manager.
"""
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# >>> CHANGE THIS to your own team name (shown in the title, required by the brief)
TEAM_NAME = "zhaoyile"

st.set_page_config(page_title="Global Superstore Sales Monitor", layout="wide")


@st.cache_data
def load_data():
    """Read the frozen Kaggle snapshot once and cache it for every widget change."""
    df = pd.read_csv("superstore.csv")
    df["Order Date"] = pd.to_datetime(df["Order Date"], format="mixed")
    df["year_month"] = df["Order Date"].dt.to_period("M").dt.to_timestamp()
    return df


df = load_data()

st.title(f"Global Superstore Sales Monitor — {TEAM_NAME}")
st.caption(
    "For the regional sales manager: review sales and profit for the region, "
    "spot loss-making product lines, and decide where to change discounting."
)

# ---------------------------------------------------------------------------
# Filters in the sidebar — the manager only ever looks after their own market,
# so the market selector is the one filter that matters most.
# ---------------------------------------------------------------------------
st.sidebar.header("Filters")
markets = sorted(df["Market"].unique())
market = st.sidebar.selectbox(
    "Market (your region)", markets, index=markets.index("US")
)

min_date, max_date = df["Order Date"].min(), df["Order Date"].max()
date_range = st.sidebar.date_input(
    "Date range", value=(min_date, max_date),
    min_value=min_date, max_value=max_date,
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = date_range
else:
    start, end = min_date, max_date

d = df[df["Market"] == market].copy()
d = d[(d["Order Date"] >= pd.Timestamp(start)) &
      (d["Order Date"] <= pd.Timestamp(end))]

# ---------------------------------------------------------------------------
# Top: at most three headline numbers — answer "is anything wrong right now?"
# ---------------------------------------------------------------------------
total_sales = d["Sales"].sum()
total_profit = d["Profit"].sum()
profit_margin = (100 * total_profit / total_sales) if total_sales else 0.0

k1, k2, k3 = st.columns(3)
k1.metric("Total sales", f"${total_sales:,.0f}")
k2.metric("Total profit", f"${total_profit:,.0f}")
k3.metric("Profit margin", f"{profit_margin:.1f}%")

# ---------------------------------------------------------------------------
# Middle: the two supporting charts that explain WHY a headline number moved.
# ---------------------------------------------------------------------------
st.subheader("Monthly sales and profit")
monthly = d.groupby("year_month")[["Sales", "Profit"]].sum()
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(monthly.index, monthly["Sales"], label="Sales", color="#1f77b4")
ax.plot(monthly.index, monthly["Profit"], label="Profit", color="#2ca02c")
ax.set_ylabel("USD")
ax.set_xlabel("Month")
ax.legend()
fig.autofmt_xdate()
st.pyplot(fig)

st.subheader("Profit by sub-category (red bars are losing money)")
sub = d.groupby("Sub-Category")["Profit"].sum().sort_values()
bar_colors = ["#d62728" if value < 0 else "#1f77b4" for value in sub.values]
fig2, ax2 = plt.subplots(figsize=(10, 5))
ax2.barh(sub.index, sub.values, color=bar_colors)
ax2.set_xlabel("Total profit (USD)")
ax2.axvline(0, color="grey", linewidth=0.8)
st.pyplot(fig2)

# ---------------------------------------------------------------------------
# Bottom: detail for a manager who wants to dig in (collapsed by default).
# ---------------------------------------------------------------------------
with st.expander("Detail: sales and profit by category"):
    detail = (d.groupby("Category")[["Sales", "Profit"]]
              .sum().round(0).sort_values("Profit", ascending=False))
    st.dataframe(detail)

st.caption(
    "Data: Jan 2011 – Dec 2014, Global Superstore (Kaggle snapshot). "
    "In production this would refresh nightly from the point-of-sale/ERP "
    "system; the manager reviews it every Monday morning."
)
