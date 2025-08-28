import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Quản lý nguyên phụ liệu", layout="wide")

# =========================
# KẾT NỐI GOOGLE SHEET
# =========================
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(creds)

SHEET_ID = "1my6VbCaAlDjVm5ITvjSV94tVU8AfR8zrHuEtKhjCAhY"   # thay bằng ID thật
sheet = client.open_by_key(SHEET_ID).sheet1

# =========================
# ĐỌC DỮ LIỆU HIỆN TẠI
# =========================
data = sheet.get_all_records()
df = pd.DataFrame(data)

st.title("📦 Quản lý nguyên phụ liệu theo mã hàng")

if df.empty:
    st.warning("Google Sheet đang rỗng, hãy thêm dữ liệu mới 👇")
else:
    # Hiển thị & chỉnh sửa từng mã hàng
    for ma_hang in df["Mã hàng"].unique():
        st.subheader(f"📌 Mã hàng: {ma_hang}")

        df_mahang = df[df["Mã hàng"] == ma_hang]
        edited_df = st.data_editor(df_mahang, num_rows="dynamic", key=f"edit_{ma_hang}")

        if st.button(f"💾 Lưu thay đổi cho {ma_hang}", key=f"save_{ma_hang}"):
            # Xóa dữ liệu cũ của mã hàng
            df_all = df[df["Mã hàng"] != ma_hang]

            # Gộp dữ liệu cũ + dữ liệu mới
            new_df = pd.concat([df_all, edited_df], ignore_index=True)

            # Clear & update lại Google Sheet
            sheet.clear()
            sheet.update([new_df.columns.values.tolist()] + new_df.values.tolist())
            st.success(f"✅ Đã lưu thay đổi cho {ma_hang}")

    st.markdown("---")

# =========================
# FORM THÊM DỮ LIỆU MỚI
# =========================
st.header("➕ Thêm mã hàng mới")

with st.form("add_new"):
    col1, col2 = st.columns(2)

    with col1:
        ma_hang_new = st.text_input("Mã hàng")
        ten_nguyen_phu_lieu = st.text_input("Tên nguyên phụ liệu")
    with col2:
        so_luong = st.number_input("Số lượng", min_value=0, step=1)
        ghi_chu = st.text_input("Ghi chú")

    submitted = st.form_submit_button("Thêm vào Google Sheet")

    if submitted:
        if not ma_hang_new:
            st.error("❌ Vui lòng nhập Mã hàng")
        else:
            # Chuẩn bị dòng mới
            new_row = {
                "Mã hàng": ma_hang_new,
                "Tên nguyên phụ liệu": ten_nguyen_phu_lieu,
                "Số lượng": so_luong,
                "Ghi chú": ghi_chu
            }

            # Append vào sheet
            sheet.append_row(list(new_row.values()))
            st.success(f"✅ Đã thêm mã hàng {ma_hang_new} vào Google Sheet")
