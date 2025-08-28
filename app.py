import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Google Sheet App", layout="wide")

# =======================
# KẾT NỐI GOOGLE SHEET
# =======================

# Lấy service account từ secrets (TOML format)
service_account_info = dict(st.secrets["gcp_service_account"])

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
client = gspread.authorize(creds)

# =======================
# ĐỌC GOOGLE SHEET
# =======================
SHEET_ID = "YOUR_SHEET_ID_HERE"   # 🔹 thay bằng ID thật của Google Sheet
sheet = client.open_by_key(SHEET_ID).sheet1

data = sheet.get_all_records()

# =======================
# HIỂN THỊ STREAMLIT
# =======================
st.title("📊 Kết nối Google Sheet với Streamlit")

if data:
    st.success("Kết nối thành công ✅")
    st.write(data)
else:
    st.warning("Google Sheet đang rỗng hoặc chưa có dữ liệu.")
