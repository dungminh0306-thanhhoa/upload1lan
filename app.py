import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Google Sheet App", layout="wide")

# =======================
# KẾT NỐI GOOGLE SHEET
# =======================
service_account_info = dict(st.secrets["gcp_service_account"])
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
client = gspread.authorize(creds)

# =======================
# ĐỌC GOOGLE SHEET
# =======================
SHEET_ID = "1my6VbCaAlDjVm5ITvjSV94tVU8AfR8zrHuEtKhjCAhY"   # 🔹 thay bằng ID thật
sheet = client.open_by_key(SHEET_ID).sheet1
data = sheet.get_all_records()

# =======================
# HIỂN THỊ STREAMLIT
# =======================
st.title("📊 Quản lý dữ liệu theo Mã hàng")

if data:
    df = pd.DataFrame(data)

    # kiểm tra có cột "Mã hàng" hay chưa
    if "Mã hàng" not in df.columns:
        st.error("❌ Không tìm thấy cột 'Mã hàng' trong Google Sheet")
    else:
        # danh sách mã hàng
        ma_hangs = df["Mã hàng"].unique()

        # chọn mã từ dropdown
        selected_ma = st.selectbox("🔎 Chọn Mã hàng:", ma_hangs)

        # lọc dữ liệu theo mã được chọn
        sub_df = df[df["Mã hàng"] == selected_ma]

        # hiển thị bảng
        st.subheader(f"📦 Mã hàng: {selected_ma}")
        st.dataframe(sub_df, use_container_width=True)
else:
    st.warning("Google Sheet rỗng hoặc chưa có dữ liệu.")
