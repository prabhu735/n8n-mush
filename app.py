import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import numpy as np

# ---------- CONFIG ----------
st.set_page_config(page_title="Mushroom Intelligence", layout="wide")

# ---------- AUTH ----------
scope = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope,
)
client = gspread.authorize(creds)

# ---------- LOAD SHEET ----------
SHEET_ID = "10a986fGptAR1LbS5NloJjvqM00LwGEWuwnmllf-MBXI"
sheet = client.open_by_key(SHEET_ID)

tabs = {ws.title: ws for ws in sheet.worksheets()}

# ---------- LOAD SALES ----------
if "Sales_Log" in tabs:
    sales = pd.DataFrame(tabs["Sales_Log"].get_all_records())
else:
    st.error("❌ Sales_Log tab not found")
    st.stop()

# ---------- CLEAN ----------
sales.columns = sales.columns.str.strip()
sales['Quantity_Sold'] = pd.to_numeric(sales['Quantity_Sold'], errors='coerce')
sales['Rate'] = pd.to_numeric(sales['Rate'], errors='coerce')

sales = sales.dropna(subset=['Quantity_Sold', 'Rate'])

sales['Total'] = sales['Quantity_Sold'] * sales['Rate']
sales['Date'] = pd.to_datetime(sales['Date'], errors='coerce')

# ---------- FILTERS ----------
st.sidebar.title("🎯 Filters")

min_date = sales['Date'].min()
max_date = sales['Date'].max()

date_range = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date]
)

filtered = sales[
    (sales['Date'] >= pd.to_datetime(date_range[0])) &
    (sales['Date'] <= pd.to_datetime(date_range[1]))
]

# ---------- KPIs ----------
total_revenue = filtered['Total'].sum()
total_qty = filtered['Quantity_Sold'].sum()
avg_price = total_revenue / total_qty if total_qty != 0 else 0

# ---------- CHART DATA ----------
daily = filtered.groupby('Date')['Total'].sum()
product_sales = filtered.groupby('Product_Type')['Total'].sum()

# ---------- ANOMALY DETECTION ----------
filtered['z_score'] = (
    (filtered['Total'] - filtered['Total'].mean()) / filtered['Total'].std()
)
anomalies = filtered[filtered['z_score'] > 2]

# ---------- UI ----------
st.title("🍄 Mushroom Intelligence Dashboard")
st.caption("Real-time farm analytics")

# ---------- TABS ----------
tab1, tab2, tab3 = st.tabs(["📊 Overview", "📈 Trends", "⚠️ Insights"])

# ---------- TAB 1: OVERVIEW ----------
with tab1:
    col1, col2, col3 = st.columns(3)

    col1.metric("💰 Revenue", f"₹{total_revenue:.0f}")
    col2.metric("📦 Quantity", f"{total_qty:.0f} kg")
    col3.metric("💵 Avg Price", f"₹{avg_price:.2f}")

# ---------- TAB 2: TRENDS ----------
with tab2:
    st.subheader("📈 Revenue Trend")
    st.line_chart(daily)

    st.subheader("📊 Product-wise Sales")
    st.bar_chart(product_sales)

# ---------- TAB 3: INSIGHTS ----------
with tab3:
    st.subheader("🧠 Smart Insights")

    if total_revenue > 20000:
        st.success("🔥 Strong revenue performance")

    if avg_price < 30:
        st.warning("⚠️ Price per kg is low")

    if total_qty < 500:
        st.info("📉 Sales volume is low")

    st.markdown("---")

    st.subheader("⚠️ Anomaly Detection")

    if not anomalies.empty:
        st.error("Unusual high sales detected")
        st.write(anomalies[['Date', 'Total']])
    else:
        st.success("No anomalies detected")

# ---------- FOOTER ----------
st.markdown("---")
st.caption("Live data from Google Sheets 🚀")
