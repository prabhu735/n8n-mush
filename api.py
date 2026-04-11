from fastapi import FastAPI
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os, json

app = FastAPI()

# ---------- AUTH (SECURE) ----------
creds_dict = json.loads(os.environ["GOOGLE_CREDS"])

creds = Credentials.from_service_account_info(
    creds_dict,
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

client = gspread.authorize(creds)

SHEET_ID = "10a986fGptAR1LbS5NloJjvqM00LwGEWuwnmllf-MBXI"

@app.get("/analyze")
def analyze():
    sheet = client.open_by_key(SHEET_ID)
    tabs = {ws.title: ws for ws in sheet.worksheets()}

    sales = pd.DataFrame(tabs["Sales_Log"].get_all_records())

    sales.columns = sales.columns.str.strip()
    sales['Quantity_Sold'] = pd.to_numeric(sales['Quantity_Sold'], errors='coerce')
    sales['Rate'] = pd.to_numeric(sales['Rate'], errors='coerce')

    sales = sales.dropna(subset=['Quantity_Sold', 'Rate'])
    sales['Total'] = sales['Quantity_Sold'] * sales['Rate']

    total_revenue = sales['Total'].sum()
    total_qty = sales['Quantity_Sold'].sum()
    avg_price = total_revenue / total_qty if total_qty != 0 else 0

    return {
        "revenue": float(total_revenue),
        "quantity": float(total_qty),
        "avg_price": float(avg_price)
    }
