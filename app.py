import streamlit as st
import pandas as pd
import os

FILE_NAME = "nguyen_phu_lieu.csv"

# Khởi tạo file nếu chưa có
if not os.path.exists(FILE_NAME):
    df = pd.DataFrame(columns=["Mã hàng", "Tên hàng", "Đơn vị", "Số lượng"])
    df.to_csv(FILE_NAME, index=False)

def load_data():
    return pd.read_csv(FILE_NAME)

def save_data(df):
    df.to_csv(FILE_NAME, index=False)

# =================== GIAO DIỆN =====================
st.set_page_config(page_title="Quản lý Nguyên Phụ Liệu", layout="wide")

st.title("📦 Quản lý Nguyên Phụ Liệu trong Kho")

menu = st.sidebar.radio("Chọn chức năng", ["Xem tồn kho", "Nhập kho", "Xuất kho", "Tìm kiếm"])

# Xem tồn kho
if menu == "Xem tồn kho":
    st.subheader("📊 Tồn kho hiện tại")
    df = load_data()
    st.dataframe(df, use_container_width=True)

# Nhập kho
elif menu == "Nhập kho":
    st.subheader("➕ Nhập kho nguyên phụ liệu")
    with st.form("form_nhap"):
        ma = st.text_input("Mã hàng")
        ten = st.text_input("Tên hàng")
        dvi = st.text_input("Đơn vị")
        sl = st.number_input("Số lượng", min_value=1, step=1)
        submit = st.form_submit_button("Thêm / Cập nhật")

        if submit:
            df = load_data()
            if ma in df["Mã hàng"].values:
                df.loc[df["Mã hàng"] == ma, "Số lượng"] += sl
            else:
                new_row = {"Mã hàng": ma, "Tên hàng": ten, "Đơn vị": dvi, "Số lượng": sl}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success(f"✅ Đã thêm/cập nhật {ten} ({ma})")

# Xuất kho
elif menu == "Xuất kho":
    st.subheader("📦 Xuất kho nguyên phụ liệu")
    with st.form("form_xuat"):
        ma = st.text_input("Mã hàng cần xuất")
        sl = st.number_input("Số lượng xuất", min_value=1, step=1)
        submit = st.form_submit_button("Xuất kho")

        if submit:
            df = load_data()
            if ma in df["Mã hàng"].values:
                so_luong = df.loc[df["Mã hàng"] == ma, "Số lượng"].values[0]
                if so_luong >= sl:
                    df.loc[df["Mã hàng"] == ma, "Số lượng"] -= sl
                    save_data(df)
                    st.success(f"✅ Đã xuất {sl} đơn vị cho mã {ma}")
                else:
                    st.error("❌ Không đủ số lượng trong kho!")
            else:
                st.error("❌ Không tìm thấy mã hàng!")

# Tìm kiếm
elif menu == "Tìm kiếm":
    st.subheader("🔍 Tìm kiếm nguyên phụ liệu")
    keyword = st.text_input("Nhập tên hàng cần tìm")
    if keyword:
        df = load_data()
        kq = df[df["Tên hàng"].str.contains(keyword, case=False, na=False)]
        if not kq.empty:
            st.dataframe(kq, use_container_width=True)
        else:
            st.warning("⚠️ Không tìm thấy kết quả")
