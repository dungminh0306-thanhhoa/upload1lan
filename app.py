import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# --- Kết nối Google Sheet ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Mở sheet
SHEET_URL = "https://docs.google.com/spreadsheets/d/1my6VbCaAlDjVm5ITvjSV94tVU8AfR8zrHuEtKhjCAhY"
sheet = client.open_by_url(SHEET_URL).sheet1

# Đọc dữ liệu
data = sheet.get_all_records()
df = pd.DataFrame(data)

# Hiển thị trên Streamlit
st.title("📊 Demo Google Sheet với Streamlit")
st.dataframe(df)
