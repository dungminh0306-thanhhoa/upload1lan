import streamlit as st

# ----------------------------
# Fake database
# ----------------------------
products = [
    {"id": 1, "name": "Áo phao nam", "price": 600000, "image": "https://i.imgur.com/3ZQ3Z4R.png"},
    {"id": 2, "name": "Áo khoác nữ", "price": 750000, "image": "https://i.imgur.com/hX6Qd8R.png"},
    {"id": 3, "name": "Áo gió", "price": 500000, "image": "https://i.imgur.com/vVnM1yM.png"},
]

# ----------------------------
# Session state setup
# ----------------------------
if "cart" not in st.session_state:
    st.session_state.cart = []
if "orders" not in st.session_state:
    st.session_state.orders = []
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# ----------------------------
# Sidebar with logo + login
# ----------------------------
st.sidebar.image("https://i.imgur.com/gnLOQYJ.png", use_container_width=True)
st.sidebar.title("Chức năng")

menu = st.sidebar.radio("Điều hướng", ["Trang chủ", "Giỏ hàng", "Đơn hàng của tôi", "Admin"])

# ----------------------------
# Login form
# ----------------------------
if not st.session_state.logged_in:
    st.sidebar.subheader("Đăng nhập")
    username = st.sidebar.text_input("Tên đăng nhập")
    password = st.sidebar.text_input("Mật khẩu", type="password")
    if st.sidebar.button("Đăng nhập"):
        if username == "admin" and password == "123":
            st.session_state.logged_in = True
            st.session_state.is_admin = True
            st.sidebar.success("Đăng nhập Admin thành công!")
        elif username != "" and password != "":
            st.session_state.logged_in = True
            st.session_state.is_admin = False
            st.sidebar.success("Đăng nhập thành công!")
        else:
            st.sidebar.error("Sai thông tin đăng nhập!")
else:
    if st.sidebar.button("Đăng xuất"):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.session_state.cart = []
        st.sidebar.success("Đã đăng xuất!")

# ----------------------------
# Trang chủ
# ----------------------------
if menu == "Trang chủ":
    st.title("🛍️ Cửa hàng Online")
    for product in products:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(product["image"], caption=product["name"], use_container_width=True)
        with col2:
            st.subheader(product["name"])
            st.write(f"💰 Giá: {product['price']:,} VND")
            qty = st.number_input("Số lượng", min_value=1, value=1, key=f"qty_{product['id']}")
            if st.button("🛒 Thêm vào giỏ", key=f"add_{product['id']}"):
                found = False
                for item in st.session_state.cart:
                    if item["id"] == product["id"]:
                        item["qty"] += qty
                        found = True
                        break
                if not found:
                    st.session_state.cart.append({
                        "id": product["id"],
                        "name": product["name"],
                        "price": product["price"],
                        "qty": qty
                    })
                st.success(f"Đã thêm {qty} {product['name']} vào giỏ!")

# ----------------------------
# Giỏ hàng
# ----------------------------
elif menu == "Giỏ hàng":
    st.title("🛒 Giỏ hàng của bạn")
    if not st.session_state.cart:
        st.info("Giỏ hàng trống!")
    else:
        total = 0
        for item in st.session_state.cart:
            st.write(f"**{item['name']}** - {item['qty']} x {item['price']:,} VND")
            total += item["qty"] * item["price"]
        st.subheader(f"Tổng cộng: {total:,} VND")
        if st.button("✅ Đặt hàng"):
            st.session_state.orders.append({
                "items": st.session_state.cart.copy(),
                "status": "Chờ xác nhận"
            })
            st.session_state.cart.clear()
            st.success("Đặt hàng thành công! Vui lòng chờ admin xác nhận.")

# ----------------------------
# Đơn hàng của tôi
# ----------------------------
elif menu == "Đơn hàng của tôi":
    st.title("📦 Đơn hàng của tôi")
    if not st.session_state.orders:
        st.info("Bạn chưa có đơn hàng nào.")
    else:
        for i, order in enumerate(st.session_state.orders):
            st.write(f"### Đơn {i+1} - Trạng thái: {order['status']}")
            for item in order["items"]:
                st.write(f"- {item['name']} x {item['qty']}")
            if order["status"] == "Chờ xác nhận":
                if st.button(f"❌ Hủy đơn {i+1}"):
                    st.session_state.orders.pop(i)
                    st.warning("Đã hủy đơn hàng.")
                    st.experimental_rerun()

# ----------------------------
# Admin quản lý đơn hàng
# ----------------------------
elif menu == "Admin":
    if not st.session_state.is_admin:
        st.error("Bạn không có quyền truy cập!")
    else:
        st.title("👨‍💼 Quản lý đơn hàng (Admin)")
        if not st.session_state.orders:
            st.info("Chưa có đơn hàng nào.")
        else:
            for i, order in enumerate(st.session_state.orders):
                st.write(f"### Đơn {i+1} - Trạng thái: {order['status']}")
                for item in order["items"]:
                    st.write(f"- {item['name']} x {item['qty']}")
                if order["status"] == "Chờ xác nhận":
                    if st.button(f"✅ Xác nhận đơn {i+1}"):
                        st.session_state.orders[i]["status"] = "Đã xác nhận"
                        st.success(f"Đơn {i+1} đã được xác nhận.")
