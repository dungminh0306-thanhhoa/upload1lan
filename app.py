import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import json, uuid, datetime

st.set_page_config(page_title="Mini Shop", page_icon="🛍️", layout="wide")

# --- Google Sheet & Drive Helpers ---
@st.cache_resource
def get_gs():
    scopes = ["https://www.googleapis.com/auth/spreadsheets",
              "https://www.googleapis.com/auth/drive.readonly"]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scopes)
    return gspread.authorize(creds)

@st.cache_resource
def get_wb():
    return get_gs().open_by_key(st.secrets["GSHEET_ID"])

@st.cache_data(ttl=60)
def fetch_products():
    ws = get_wb().worksheet("Products")
    rows = ws.get_all_records()
    prods = []
    for r in rows:
        imgs = [s.strip() for s in r.get("image", "").split(";") if s.strip()]
        prods.append({
            "id": str(r.get("ID", "")).strip(),
            "name": r.get("NAME", ""),
            "price": int(r.get("PRICE", 0)),
            "images": imgs
        })
    return prods

@st.cache_data(ttl=30)
def fetch_orders():
    ws = get_wb().worksheet("Orders")
    rows = ws.get_all_records()
    return rows

def append_order(o):
    ws = get_wb().worksheet("Orders")
    ws.append_row([
        o["order_id"], o["user"], o["time"], o["status"],
        json.dumps(o["items"], ensure_ascii=False), o["total"]
    ])

def update_order_status(idx, status):
    ws = get_wb().worksheet("Orders")
    ws.update_cell(idx + 2, 4, status)  # row offset

# --- Drive Image Helpers ---
def extract_id(s: str):
    if "drive.google.com" in s:
        if "/file/d/" in s:
            return s.split("/file/d/")[1].split("/")[0]
        if "id=" in s:
            return s.split("id=")[1].split("&")[0]
    return s

def thumb_url(fid, w=800):
    return f"https://drive.google.com/thumbnail?id={fid}&sz=w{w}"

def view_url(fid):
    return f"https://drive.google.com/uc?export=view&id={fid}"

# --- Session State ---
for key in ("cart", "username", "logged_in", "is_admin"):
    if key not in st.session_state:
        st.session_state[key] = "" if key == "username" else False
st.session_state.cart = st.session_state.get("cart", [])
st.session_state.cart = st.session_state.cart or []

# --- Sidebar ---
logo_id = None  # nếu muốn logo từ Drive, đặt ID vào đây
if logo_id:
    st.sidebar.image(view_url(extract_id(logo_id)), use_container_width=True)
st.sidebar.markdown("## Tài khoản")
if not st.session_state.logged_in:
    u = st.sidebar.text_input("Tên đăng nhập")
    p = st.sidebar.text_input("Mật khẩu", type="password")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Đăng nhập khách"):
            if u.strip():
                st.session_state.username = u.strip()
                st.session_state.logged_in = True
                st.success(f"Xin chào {u}")
                st.rerun()
    with col2:
        if st.button("Đăng nhập Admin"):
            if u == "admin" and p == "123":
                st.session_state.username = "admin"
                st.session_state.is_admin = True
                st.session_state.logged_in = True
                st.success("Đăng nhập Admin")
                st.rerun()
            else:
                st.error("Sai mật khẩu")
else:
    st.sidebar.write(f"Đăng nhập: {st.session_state.username}")
    if st.sidebar.button("Đăng xuất"):
        for k in ["logged_in","is_admin","username","cart"]:
            st.session_state[k] = "" if k=="username" else False if k!="cart" else []
        st.success("Đã đăng xuất")
        st.rerun()

orders = fetch_orders()
pending = sum(1 for o in orders if o.get("status","")=="Chờ xác nhận")
if st.session_state.is_admin and pending:
    st.sidebar.error(f"🔔 {pending} đơn chờ xác nhận")

menu = st.sidebar.radio(
    "Menu",
    ["Trang chủ", "Giỏ hàng", "Đơn của tôi"] + (["Quản lý đơn"] if st.session_state.is_admin else [])
)

# --- Pages ---
prods = fetch_products()

if menu == "Trang chủ":
    st.title("🛍️ Sản phẩm")
    cols = st.columns(2)
    for i, p in enumerate(prods):
        with cols[i % 2]:
            if p["images"]:
                fid = extract_id(p["images"][0])
                st.image(thumb_url(fid), caption=p["name"], use_container_width=True)
            st.markdown(f"**{p['name']}**")
            st.write(f"{p['price']:,} VND")
            qty = st.number_input("Số lượng", 1, 1, key=f"p{p['id']}")
            if st.button("Thêm vào giỏ", key=f"a{p['id']}"):
                exists = next((i for i in st.session_state.cart if i["id"]==p["id"]),None)
                if exists:
                    exists["qty"] += qty
                else:
                    st.session_state.cart.append({"id":p["id"],"name":p["name"],"price":p["price"],"qty":qty})
                st.success("Đã thêm vào giỏ")

elif menu == "Giỏ hàng":
    st.title("🛒 Giỏ hàng")
    if not st.session_state.cart:
        st.info("Giỏ hàng trống")
    else:
        total = 0
        rm = []
        for i, item in enumerate(st.session_state.cart):
            c1, c2, c3 = st.columns([3,2,1])
            c1.write(f"{item['name']}")
            item["qty"] = c2.number_input("Qty", 1, item["qty"], key=f"c{i}")
            c3.write(f"{item['qty']*item['price']:,} VND")
            total += item["qty"]*item["price"]
            if c3.button("❌", key=f"r{i}"):
                rm.append(i)
        for i in reversed(rm):
            st.session_state.cart.pop(i)
            st.rerun()
        st.subheader(f"Tổng: {total:,} VND")
        if st.button("Đặt hàng"):
            order = {
                "order_id": str(uuid.uuid4())[:8],
                "user": st.session_state.username or "Khách",
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "Chờ xác nhận",
                "items": st.session_state.cart.copy(),
                "total": total
            }
            append_order(order)
            st.session_state.cart.clear()
            st.success(f"Đặt thành công! Mã đơn: {order['order_id']}")
            st.rerun()

elif menu == "Đơn của tôi":
    st.title("🧾 Đơn của tôi")
    me = st.session_state.username or "Khách"
    my = [o for o in orders if o["user"]==me]
    if not my:
        st.info("Chưa có đơn")
    else:
        for o in my:
            with st.expander(f"{o['order_id']} • {o['time']} • {o['status']}"):
                for it in o["items"]:
                    st.write(f"- {it['name']} x {it['qty']} = {it['price']*it['qty']:,} VND")
                st.write(f"**Tổng**: {o['total']:,} VND")
                if o["status"]=="Chờ xác nhận":
                    if st.button("Hủy đơn", key=f"c{o['order_id']}"):
                        update_order_status(orders.index(o), "Đã hủy")
                        st.warning("Đã hủy")
                        st.rerun()

elif menu == "Quản lý đơn":
    st.title("📋 Quản lý đơn (Admin)")
    if not orders:
        st.info("Không có đơn")
    else:
        for idx, o in enumerate(orders):
            with st.expander(f"{o['order_id']} • {o['user']} • {o['time']} • {o['status']}"):
                for it in o["items"]:
                    st.write(f"- {it['name']} x {it['qty']} = {it['price']*it['qty']:,} VND")
                st.write(f"**Tổng:** {o['total']:,} VND")
                if o['status']=="Chờ xác nhận":
                    c1, c2 = st.columns(2)
                    if c1.button("✅ Xác nhận", key=f"k{o['order_id']}"):
                        update_order_status(idx, "Đã xác nhận")
                        st.success("Đã xác nhận")
                        st.rerun()
                    if c2.button("❌ Hủy", key=f"d{o['order_id']}"):
                        update_order_status(idx, "Đã hủy")
                        st.warning("Đã hủy")
                        st.rerun()
