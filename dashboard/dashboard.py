# dashboard.py
import os
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

st.set_page_config(
    page_title="E-Commerce Real-Time Dashboard",
    page_icon=":bar_chart:",
    layout="wide"
)

# Get API URL from environment variables; default to localhost if not set
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8080")

@st.cache_data(ttl=30)
def get_all_transactions():
    try:
        response = requests.get(f"{API_BASE_URL}/transactions/all")
        response.raise_for_status()
        data = response.json().get("all_transactions", [])
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error fetching transactions: {e}")
        return pd.DataFrame()

# Auto-refresh every 30 seconds
refresh_count = st_autorefresh(interval=30 * 1000, key="dashboard_autorefresh")
st.write("Refresh count:", refresh_count)

df_all = get_all_transactions()
if df_all.empty:
    st.error("No transaction data available.")
    st.stop()

df_all["timestamp"] = pd.to_datetime(df_all["timestamp"])

st.sidebar.header("Filter Options")
unique_categories = sorted(df_all["product_category"].unique())
unique_payment_methods = sorted(df_all["payment_method"].unique())

selected_categories = st.sidebar.multiselect("Select Product Categories", options=unique_categories, default=unique_categories)
selected_payment_methods = st.sidebar.multiselect("Select Payment Methods", options=unique_payment_methods, default=unique_payment_methods)

df_filtered = df_all[
    (df_all["product_category"].isin(selected_categories)) &
    (df_all["payment_method"].isin(selected_payment_methods))
]

st.title("E-Commerce Real-Time Dashboard")

col1, col2, col3 = st.columns(3)
with col1:
    total_revenue = df_all["order_total"].sum()
    st.metric("Total Revenue", f"${total_revenue:,.2f}")
with col2:
    total_tx = df_all.shape[0]
    discounted_tx = df_all[df_all["discount_percent"] > 0].shape[0]
    discount_percentage = (discounted_tx / total_tx * 100) if total_tx > 0 else 0
    st.metric("Discount Usage", f"{discount_percentage:.1f}%")
    st.caption(f"{discounted_tx} of {total_tx} transactions had a discount.")
with col3:
    aov = total_revenue / total_tx if total_tx > 0 else 0
    st.metric("Average Order Value", f"${aov:,.2f}")

st.markdown("---")
st.subheader("Latest 10 Transactions")
df_latest = df_filtered.sort_values("timestamp", ascending=False).head(10)
st.dataframe(df_latest, use_container_width=True)

st.markdown("---")
st.subheader("Daily Revenue Over Time")
df_all["day"] = df_all["timestamp"].dt.date
df_revenue = df_all.groupby("day")["order_total"].sum().reset_index()
df_revenue["day"] = pd.to_datetime(df_revenue["day"])
if not df_revenue.empty:
    fig_revenue = px.line(df_revenue, x="day", y="order_total", title="Daily Revenue", labels={"day": "Date", "order_total": "Revenue ($)"})
    st.plotly_chart(fig_revenue, use_container_width=True)
else:
    st.write("No revenue data available.")

st.markdown("---")
st.subheader("Revenue by Product (Filtered)")
if not df_filtered.empty:
    df_product = df_filtered.groupby(["product_id", "product_category"], as_index=False)["order_total"].sum()
    df_product.rename(columns={"order_total": "total_revenue"}, inplace=True)
    fig_product = px.bar(df_product, x="product_id", y="total_revenue", color="product_category", title="Revenue by Product", labels={"product_id": "Product ID", "total_revenue": "Revenue ($)"})
    st.plotly_chart(fig_product, use_container_width=True)
else:
    st.write("No data available for product revenue.")

st.markdown("---")
col_cat, col_pay = st.columns(2)
with col_cat:
    st.subheader("Revenue by Product Category")
    if not df_filtered.empty:
        df_category = df_filtered.groupby("product_category")["order_total"].sum().reset_index()
        df_category.rename(columns={"order_total": "revenue"}, inplace=True)
        fig_category = px.bar(df_category, x="product_category", y="revenue", title="Revenue by Category", labels={"product_category": "Category", "revenue": "Revenue ($)"})
        st.plotly_chart(fig_category, use_container_width=True)
    else:
        st.write("No category data available.")
with col_pay:
    st.subheader("Payment Method Distribution")
    if not df_filtered.empty:
        df_payment = df_filtered.groupby("payment_method")["order_total"].count().reset_index()
        df_payment.rename(columns={"order_total": "count"}, inplace=True)
        fig_payment = px.pie(df_payment, names="payment_method", values="count", title="Payment Method Distribution")
        st.plotly_chart(fig_payment, use_container_width=True)
    else:
        st.write("No payment method data available.")

with st.sidebar:
    st.header("Dashboard Controls")
    if st.button("Manual Refresh"):
        st.rerun()
