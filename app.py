import streamlit as st

# ==============================
# Ảnh sản phẩm (Google Drive)
# ==============================
IMAGE_LINKS = {
    1: "https://drive.google.com/uc?export=view&id=1s6sJALOs2IxX5f9nqa4Tf8zut_U9KE3O",
    2: "https://drive.google.com/uc?export=view&id=1UpNF_Fd5gWbrtEliUbD7KDRilpcnQK3H",
    3: "https://drive.google.com/uc?export=view&id=1hZ2skulhj5YB1EOV1ElcAQG9bRe-m8Ta",
    4: "https://drive.google.com/uc?export=view&id=1tfyYp_9L2GU5zUh3w_GSvfcpa_hNlJUk",
    5: "https://drive.google.com/uc?export=view&id=144OpPO0kfqMUUuNga8LJIFwqnNlYQMQG"
}

# ==============================
# Danh sách sản phẩm
# ==============================
products = [
    {"id": 1, "name": "Quần bơi",   "price": 120000},
    {"id": 2, "name": "Quần sịp",   "price": 250000},
    {"id": 3, "name": "Áo khoác",   "price": 350000},
    {"id": 4, "name": "Áo ba lỗ",   "price": 450000},
    {"id": 5, "name": "Áo gòn",     "price": 600000},
]

# Gán ảnh từ IMAGE_LINKS
for p in products:
    p["image"] = IMAGE_LINKS.get(p["id"], "")

# ==============================
# Khởi tạo session
# ==============================
if "cart" not in st.session_state:
    st.session_state.cart = []
if "orders" not in st.session_state:
    st.session_state.orders = []
if "new_order" not in st.session_state:
    st.session_state.new_order = False

# ==============================
# Sidebar Logo + Menu
# ==============================
st.sidebar.image("https://i.imgur.com/gnLOQYJ.png", use_column_width=True)  # logo công ty
page = st.sidebar.radio("Menu", ["Trang chủ", "Giỏ hàng", "Đơn hàng của tôi", "Admin"])

# ==============================
# Hàm xử lý giỏ hàng
# ==============================
def add_to_cart(product, qty):
    for item in st.session_state.cart:
        if item["id"] == product["id"]:
            item["qty"] += qty
            return
    st.session_state.cart.append({"id": product["id"], "name": product["name"], "price": product["price"], "qty": qty})

def place_order():
    if not st.session_state.cart:
        st.warning("Giỏ hàng trống!")
        return
    st.session_state.orders.append({"items": st.session_state.cart.copy()})
    st.session_state.cart.clear()
    st.session_state.new_order = True
    st.success("Đặt hàng thành công!")

# ==============================
# Trang chủ
# ==============================
if page == "Trang chủ":
    st.header("🛍️ Sản phẩm")
    cols = st.columns(3)

    for idx, product in enumerate(products):
        with cols[idx % 3]:
            st.image(product["image"], caption=product["name"], use_column_width=True)
            st.write(f"💰 {product['price']:,} VND")
            qty = st.number_input(f"Số lượng ({product['name']})", min_value=1, value=1, key=f"qty_{product['id']}")
            if st.button("Thêm vào giỏ", key=f"add_{product['id']}"):
                add_to_cart(product, qty)
                st.success(f"✅ Đã thêm {qty} x {product['name']} vào giỏ")

# ==============================
# Giỏ hàng
# ==============================
elif page == "Giỏ hàng":
    st.header("🛒 Giỏ hàng của bạn")
    if not st.session_state.cart:
        st.info("Giỏ hàng trống!")
    else:
        total = 0
        for item in st.session_state.cart:
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.write(item["name"])
            with col2:
                qty = st.number_input("Số lượng", min_value=1, value=item["qty"], key=f"edit_{item['id']}")
                item["qty"] = qty
            with col3:
                st.write(f"{item['price']:,} VND")
            with col4:
                st.write(f"{item['qty'] * item['price']:,} VND")
            total += item["qty"] * item["price"]

        st.subheader(f"💵 Tổng cộng: {total:,} VND")
        if st.button("Đặt hàng"):
            place_order()

# ==============================
# Đơn hàng của tôi
# ==============================
elif page == "Đơn hàng của tôi":
    st.header("📦 Đơn hàng của tôi")
    if not st.session_state.orders:
        st.info("Bạn chưa có đơn hàng nào.")
    else:
        for i, order in enumerate(st.session_state.orders, 1):
            st.write(f"### Đơn hàng #{i}")
            for item in order["items"]:
                st.write(f"- {item['qty']} x {item['name']} ({item['price']:,} VND)")
            total = sum(item["qty"] * item["price"] for item in order["items"])
            st.write(f"**Tổng: {total:,} VND**")

# ==============================
# Admin
# ==============================
elif page == "Admin":
    st.header("🛠️ Quản lý đơn hàng (Admin)")
    if st.session_state.new_order:
        st.success("🔔 Có đơn hàng mới!")
        st.session_state.new_order = False

    if not st.session_state.orders:
        st.info("Chưa có đơn hàng nào.")
    else:
        for i, order in enumerate(st.session_state.orders, 1):
            st.write(f"### Đơn hàng #{i}")
            for item in order["items"]:
                st.write(f"- {item['qty']} x {item['name']} ({item['price']:,} VND)")
            total = sum(item["qty"] * item["price"] for item in order["items"])
            st.write(f"**Tổng: {total:,} VND**")
