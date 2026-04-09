import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ---------- CONFIG ----------
st.set_page_config(page_title="Mushroom Dashboard", layout="wide")

# ---------- AUTH ----------
scope = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope,
)
client = gspread.authorize(creds)

SHEET_ID = "10a986fGptAR1LbS5NloJjvqM00LwGEWuwnmllf-MBXI"
sheet = client.open_by_key(SHEET_ID)

# ---------- LOAD AVAILABLE TABS ----------
tabs = {ws.title: ws for ws in sheet.worksheets()}

st.write("📄 Available Tabs:", list(tabs.keys()))

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

# ---------- KPIs ----------
total_revenue = sales['Total'].sum()
total_qty = sales['Quantity_Sold'].sum()
avg_price = total_revenue / total_qty if total_qty != 0 else 0

# ---------- UI ----------
st.title("🍄 Mushroom Farm Dashboard")

col1, col2, col3 = st.columns(3)

col1.metric("💰 Total Revenue", f"₹{total_revenue:.0f}")
col2.metric("📦 Total Quantity", f"{total_qty:.0f} kg")
col3.metric("💵 Avg Price", f"₹{avg_price:.2f}")

st.markdown("---")

# ---------- CHART ----------
st.subheader("📈 Revenue Trend")

sales['Date'] = pd.to_datetime(sales['Date'], errors='coerce')
daily = sales.groupby('Date')['Total'].sum()

st.line_chart(daily)

# ---------- OPTIONAL EXTRA TABS ----------
st.markdown("---")
st.subheader("📊 Additional Data")

if "Expense_Log" in tabs:
    expenses = pd.DataFrame(tabs["Expense_Log"].get_all_records())
    expenses['Amount'] = pd.to_numeric(expenses['Amount'], errors='coerce')
    total_cost = expenses['Amount'].sum()
    st.metric("💸 Total Cost", f"₹{total_cost:.0f}")

if "Production" in tabs:
    production = pd.DataFrame(tabs["Production"].get_all_records())
    st.write("🍄 Production Data", production.head())

# ---------- INSIGHTS ----------
st.markdown("---")
st.subheader("🧠 Insights")

if total_revenue > 0:
    st.success("📈 Business is generating revenue")

if avg_price < 30:
    st.warning("⚠️ Low pricing — consider increasing rate")

st.caption("Live data from Google Sheets")
