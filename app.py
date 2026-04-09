import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ---------- CONFIG ----------
st.set_page_config(page_title="Mushroom Intelligence", layout="wide")

# ---------- AUTH ----------
scope = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope,
)
client = gspread.authorize(creds)

SHEET_NAME = "Dashboards"

# ---------- LOAD DATA ----------
sales = pd.DataFrame(client.open(SHEET_NAME).worksheet("Sales_Log").get_all_records())
production = pd.DataFrame(client.open(SHEET_NAME).worksheet("Production_Log").get_all_records())
wastage = pd.DataFrame(client.open(SHEET_NAME).worksheet("Wastage_Log").get_all_records())
expenses = pd.DataFrame(client.open(SHEET_NAME).worksheet("Expense_Log").get_all_records())

# ---------- CLEAN ----------
def clean(df):
    df.columns = df.columns.str.strip()
    return df

sales, production, wastage, expenses = map(clean, [sales, production, wastage, expenses])

sales['Quantity_Sold'] = pd.to_numeric(sales['Quantity_Sold'], errors='coerce')
sales['Rate'] = pd.to_numeric(sales['Rate'], errors='coerce')
production['Quantity_Produced'] = pd.to_numeric(production['Quantity_Produced'], errors='coerce')
wastage['Quantity_Wasted'] = pd.to_numeric(wastage['Quantity_Wasted'], errors='coerce')
expenses['Amount'] = pd.to_numeric(expenses['Amount'], errors='coerce')

sales['Total'] = sales['Quantity_Sold'] * sales['Rate']

# ---------- KPIs ----------
total_revenue = sales['Total'].sum()
total_cost = expenses['Amount'].sum()
profit = total_revenue - total_cost
roi = profit / total_cost if total_cost != 0 else 0

total_production = production['Quantity_Produced'].sum()
total_wastage = wastage['Quantity_Wasted'].sum()

wastage_percent = (total_wastage / total_production) * 100 if total_production != 0 else 0
efficiency = (sales['Quantity_Sold'].sum() / total_production) * 100 if total_production != 0 else 0

# ---------- UI ----------
st.title("🍄 Mushroom Intelligence Dashboard")

col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Revenue", f"₹{total_revenue:.0f}")
col2.metric("💸 Cost", f"₹{total_cost:.0f}")
col3.metric("📈 Profit", f"₹{profit:.0f}")
col4.metric("ROI", f"{roi*100:.2f}%")

st.markdown("---")

st.subheader("📈 Sales Trend")
sales['Date'] = pd.to_datetime(sales['Date'])
daily_sales = sales.groupby('Date')['Total'].sum()
st.line_chart(daily_sales)

st.markdown("---")

st.subheader("🧠 Insights")

if wastage_percent > 10:
    st.warning("⚠️ High wastage detected")

if roi < 0:
    st.error("❌ Loss detected")

if efficiency > 80:
    st.success("🔥 High efficiency")
