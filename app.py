import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# =========================
# HÀM TIỆN ÍCH
# =========================
def gdrive_to_direct(link):
    """Chuyển link Google Drive thành link ảnh trực tiếp"""
    if "drive.google.com" in link and "/file/d/" in link:
        fid = link.split("/file/d/")[1].split("/")[0]
        return f"https://drive.google.com/uc?export=view&id={fid}"
    return link

# =========================
# ĐỌC GOOGLE SHEET
# =========================
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Lấy credentials từ secrets (local hoặc Streamlit Cloud)
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPE)
client = gspread.authorize(creds)

# URL Google Sheet chứa sản phẩm
SHEET_URL = "https://docs.google.com/spreadsheets/d/1my6VbCaAlDjVm5ITvjSV94tVU8AfR8zrHuEtKhjCAhY/edit?usp=sharing"
sheet = client.open_by_url(SHEET_URL).sheet1
records = sheet.get_all_records()
products_df = pd.DataFrame(records)

# Chuẩn hóa link ảnh
products_df["image"] = products_df["image"].apply(gdrive_to_direct)

# =========================
# SESSION STATE
# =========================
if "cart" not in st.session_state:
    st.session_state.cart = {}
if "orders" not in st.session_state:
    st.session_state.orders = []
if "user" not in st.session_state:
    st.session_state.user = "guest"

# =========================
# GIAO DIỆN
# =========================
st.title("🛒 Cửa hàng Online")

menu = st.sidebar.radio("Chức năng", ["Mua sắm", "Giỏ hàng", "Đơn hàng của tôi", "Quản lý"])

# =========================
# MUA SẮM
# =========================
if menu == "Mua sắm":
    st.header("Sản phẩm")
    for _, p in products_df.iterrows():
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(p["image"], width=150)
        with col2:
            st.write(f"**{p['name']}** — {int(p['price']):,} VND")
            qty = st.number_input(f"Số lượng {p['name']}", min_value=1, value=1, key=f"qty_{p['id']}")
            if st.button(f"🛍️ Thêm {p['name']} vào giỏ", key=f"add_{p['id']}"):
                st.session_state.cart.setdefault(p['id'], {"product": dict(p), "qty": 0})
                st.session_state.cart[p['id']]["qty"] += qty
                st.success(f"Đã thêm {qty} x {p['name']} vào giỏ!")

# =========================
# GIỎ HÀNG
# =========================
elif menu == "Giỏ hàng":
    st.header("🛒 Giỏ hàng")
    if not st.session_state.cart:
        st.info("Giỏ hàng trống.")
    else:
        total = 0
        for pid, item in list(st.session_state.cart.items()):
            p = item["product"]
            qty = st.number_input(f"{p['name']}", min_value=1, value=item["qty"], key=f"cart_qty_{pid}")
            st.session_state.cart[pid]["qty"] = qty
            st.write(f"Giá: {int(p['price']):,} VND | Thành tiền: {int(p['price']) * qty:,} VND")
            total += int(p["price"]) * qty

        st.write(f"### Tổng cộng: {total:,} VND")

        if st.button("✅ Đặt hàng"):
            st.session_state.orders.append({
                "items": st.session_state.cart.copy(),
                "status": "Chờ xác nhận"
            })
            st.session_state.cart.clear()
            st.success("Đã đặt hàng thành công!")

# =========================
# ĐƠN HÀNG KHÁCH
# =========================
elif menu == "Đơn hàng của tôi":
    st.header("📦 Đơn hàng của tôi")
    if not st.session_state.orders:
        st.info("Bạn chưa có đơn hàng nào.")
    else:
        for i, order in enumerate(st.session_state.orders):
            st.write(f"### Đơn hàng #{i+1} - Trạng thái: {order['status']}")
            for pid, item in order["items"].items():
                p = item["product"]
                st.write(f"- {p['name']} x {item['qty']} ({int(p['price']):,} VND)")

            if order["status"] == "Chờ xác nhận":
                if st.button(f"❌ Huỷ đơn #{i+1}", key=f"cancel_{i}"):
                    st.session_state.orders[i]["status"] = "Đã huỷ"
                    st.warning(f"Bạn đã huỷ đơn #{i+1}")

# =========================
# QUẢN LÝ (ADMIN)
# =========================
elif menu == "Quản lý":
    st.header("👨‍💼 Quản lý cửa hàng")

    if st.session_state.user != "admin":
        with st.form("login_form"):
            username = st.text_input("Tài khoản")
            password = st.text_input("Mật khẩu", type="password")
            login_btn = st.form_submit_button("Đăng nhập")
            if login_btn:
                if username == "admin" and password == "123":
                    st.session_state.user = "admin"
                    st.success("Đăng nhập thành công!")
                else:
                    st.error("Sai tài khoản hoặc mật khẩu.")
    else:
        st.success("Bạn đang đăng nhập với quyền quản lý.")
        if not st.session_state.orders:
            st.info("Chưa có đơn hàng nào.")
        else:
            for i, order in enumerate(st.session_state.orders):
                st.write(f"### Đơn hàng #{i+1} - Trạng thái: {order['status']}")
                for pid, item in order["items"].items():
                    p = item["product"]
                    st.write(f"- {p['name']} x {item['qty']} ({int(p['price']):,} VND)")

                if order["status"] == "Chờ xác nhận":
                    if st.button(f"✅ Xác nhận đơn #{i+1}", key=f"confirm_{i}"):
                        st.session_state.orders[i]["status"] = "Đã xác nhận"
                        st.success(f"Đơn #{i+1} đã được xác nhận")
                    if st.button(f"❌ Từ chối đơn #{i+1}", key=f"reject_{i}"):
                        st.session_state.orders[i]["status"] = "Bị từ chối"
                        st.warning(f"Đơn #{i+1} đã bị từ chối")
