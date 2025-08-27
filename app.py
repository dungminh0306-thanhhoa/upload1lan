# ==============================
# Kho ảnh tập trung
# ==============================
IMAGE_LINKS = {
    1: "https://drive.google.com/file/d/1s6sJALOs2IxX5f9nqa4Tf8zut_U9KE3O/view?usp=drive_link",
    2: "https://drive.google.com/file/d/1UpNF_Fd5gWbrtEliUbD7KDRilpcnQK3H/view?usp=drive_link",
    3: "https://drive.google.com/file/d/1hZ2skulhj5YB1EOV1ElcAQG9bRe-m8Ta/view?usp=drive_link",
    4: "https://drive.google.com/file/d/1tfyYp_9L2GU5zUh3w_GSvfcpa_hNlJUk/view?usp=drive_link",
    5: "https://drive.google.com/file/d/144OpPO0kfqMUUuNga8LJIFwqnNlYQMQG/view?usp=drive_link"
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

# Gán ảnh tự động từ IMAGE_LINKS
for p in products:
    p["image"] = IMAGE_LINKS.get(p["id"], "")
