# test_sheets.py
import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]

creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
gc = gspread.authorize(creds)

# Thay ID bằng ID sheet của bạn
SHEET_ID = "1my6VbCaAlDjVm5ITvjSV94tVU8AfR8zrHuEtKhjCAhY"
wb = gc.open_by_key(SHEET_ID)
print("Worksheets:", [ws.title for ws in wb.worksheets()])

# Đọc sheet 'Products' (ví dụ)
ws = wb.worksheet("Products")
print(ws.get_all_records()[:3])
