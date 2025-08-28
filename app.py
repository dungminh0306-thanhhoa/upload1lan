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
SHEET_ID = "1my6VbCaAlDjVm5ITvjSV94tVU8AfR8zrHuEtKhjCAhY"   # thay bằng ID thật
sheet = client.open_by_key(SHEET_ID).sheet1
data = sheet.get_all_records()

st.title("📊 Quản lý dữ liệu theo mã")

if data:
    df = pd.DataFrame(data)

    # =======================
    # FORM NHẬP LIỆU
    # =======================
    st.subheader("✍️ Nhập dữ liệu mới")
    with st.form("input_form"):
        ma_hang = st.text_input("Mã hàng")
        ten_sp = st.text_input("Tên sản phẩm")
        so_luong = st.number_input("Số lượng", min_value=0, step=1)
        gia = st.number_input("Đơn giá", min_value=0, step=1000)
        
        submitted = st.form_submit_button("➕ Thêm dữ liệu")

        if submitted:
            # Thêm vào cuối Google Sheet
            new_row = [ma_hang, ten_sp, so_luong, gia]
            sheet.append_row(new_row)
            st.success(f"✅ Đã thêm: {new_row}")
            st.experimental_rerun()  # load lại trang để cập nhật bảng

    # =======================
    # HIỂN THỊ BẢNG THEO MÃ
    # =======================
    if "Mã hàng" not in df.columns:
        st.error("❌ Không tìm thấy cột 'Mã hàng' trong Google Sheet")
    else:
        ma_hangs = df["Mã hàng"].unique()
        for ma in ma_hangs:
            st.subheader(f"📦 Mã hàng: {ma}")
            sub_df = df[df["Mã hàng"] == ma]
            st.dataframe(sub_df, use_container_width=True)
            st.markdown("---")
else:
    st.warning("Google Sheet rỗng hoặc chưa có dữ liệu.")
