import streamlit as st
import pandas as pd
import datetime
import gspread

# ตั้งค่าหน้าตาของแอปให้เป็นแนวกว้างและธีมสะอาดตา
st.set_page_config(page_title="ระบบจดออเดอร์ร้านก๋วยจั๊บ", layout="wide")

# สไตล์ CSS ตกแต่งสไตล์มินิมอล โทนสีขาว เทา ดำ
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    h1, h2, h3 { color: #212529; font-family: 'Helvetica Neue', sans-serif; }
    .stButton>button { background-color: #212529; color: white; border-radius: 5px; width: 100%; }
    .stButton>button:hover { background-color: #495057; color: white; }
    </style>
""", unsafe_allow_html=True)

# ฝังลิงก์ Google Sheets ของคุณลงในโค้ดโดยตรง
SHEET_URL = "https://docs.google.com/spreadsheets/d/1wh7K03kwanBF4fEP1SnKjHBJIHSJK-aMQPXGjQBdW1E/edit?usp=sharing"

def get_google_sheet():
    try:
        # เชื่อมต่อผ่านลิงก์สาธารณะ (ทำงานเร็วและไม่ติดปัญหาสิทธิ์ซ้อนทับของ Streamlit)
        gc = gspread.public(SHEET_URL)
        # เจาะจงเข้าแผ่นงานที่ชื่อ orders
        worksheet = gc.worksheet("orders")
        return worksheet
    except Exception as e:
        st.error(f"⚠️ ระบบยังเข้าถึง Google Sheets ไม่ได้: {e}")
        return None

worksheet = get_google_sheet()

# ดึงข้อมูลมาทำสถิติหน้ารายงาน
if worksheet:
    try:
        data = worksheet.get_all_records()
        df_existing = pd.DataFrame(data)
    except:
        df_existing = pd.DataFrame(columns=["วันที่", "เวลา", "เมนู", "จำนวน", "ท็อปปิ้ง", "รูปแบบ", "การชำระเงิน", "โน้ต", "ราคา"])
else:
    df_existing = pd.DataFrame(columns=["วันที่", "เวลา", "เมนู", "จำนวน", "ท็อปปิ้ง", "รูปแบบ", "การชำระเงิน", "โน้ต", "ราคา"])

# คลังข้อมูลเมนูและท็อปปิ้ง
MENU = {
    "ก๋วยจั๊บธรรมดา": 50, "ก๋วยจั๊บสาหร่าย": 55, "ก๋วยจั๊บหมูเด้ง": 55,
    "ก๋วยจั๊บหมูเด้งสาหร่าย": 60, "ก๋วยจั๊บเล้ง": 60, "ก๋วยจั๊บตีนไก่": 60,
    "ก๋วยจั๊บน่องไก่": 60, "ก๋วยจั๊บทะเล": 60, "ก๋วยจั๊บเล้งสาหร่าย": 65,
    "ก๋วยจั๊บหน้าล้น": 70, "ก๋วยจั๊บรวมพิเศษ": 75, "ก๋วยจั๊บต้มยำทะเลน้ำข้น": 75
}

TOPPINGS = {
    "พิเศษ": 10, "ไข่": 10, "หมูเด้ง": 10, "หมูสับ": 10, "หมูยอ": 10,
    "กุ้ง": 10, "หมึก": 10, "ปูอัด": 10, "เล้ง": 10, "น่อง": 10,
    "ตีนไก่": 10, "เลือด": 5, "สาหร่าย": 5, "หอมเจียว": 5, "เส้น": 5
}

STOCK_ITEMS = ["เลือด", "เส้น", "หมูสับ", "กุ้ง", "หมูยอ", "หมึก", "หมูเด้ง", "สาหร่าย", "ไข่", "น้ำมะนาว", "หอมเจียว", "ตะเกียบ", "มาม่า"]

if 'need_to_buy' not in st.session_state: st.session_state.need_to_buy = []

st.title("🍜 ระบบจัดการร้านก๋วยจั๊บ (ซิงค์ตรงผ่านลิงก์ชีต)")
st.caption(f"วันที่ใช้งาน: {datetime.date.today().strftime('%d/%m/%Y')}")

tab1, tab2, tab3 = st.tabs(["🛒 รับออเดอร์ใหม่", "📊 สรุปยอดและสถิติ", "📦 เช็คสต็อกของในร้าน"])

with tab1:
    st.subheader("เพิ่มรายการอาหาร")
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_menu = st.selectbox("เลือกเมนูหลัก:", list(MENU.keys()))
        base_price = MENU[selected_menu]
        st.write(f"ราคาเริ่มต้น: **{base_price} บาท**")
        selected_toppings = st.multiselect("เพิ่มท็อปปิ้ง:", list(TOPPINGS.keys()))
        topping_price = sum([TOPPINGS[tp] for tp in selected_toppings])
        quantity = st.number_input("จำนวน (ชาม):", min_value=1, value=1, step=1)
        order_note = st.text_input("โน้ตเพิ่มเติม (เช่น ไม่เจียว, เผ็ดน้อย):", "")
    with col2:
        service_type = st.radio("รูปแบบการเสิร์ฟ:", ["ทานที่ร้าน", "กลับบ้าน"])
        payment_type = st.radio("ช่องทางการชำระเงิน:", ["เงินสด", "เงินโอน", "ไทยช่วยไทย", "แกร้ป"])
        
        total_item_price = (base_price + topping_price) * quantity
        if payment_type == "แกร้ป":
            total_item_price = st.number_input("ระบุราคา Grab สุทธิ (บาท):", min_value=0, value=int(total_item_price))
            
        st.markdown(f"### ราคารวมออเดอร์นี้: `{total_item_price}` บาท")
        
        if st.button("➕ บันทึกออเดอร์"):
            if worksheet:
                new_row = [
                    datetime.date.today().strftime("%Y-%m-%d"),
                    datetime.datetime.now().strftime("%H:%M:%S"),
                    selected_menu,
                    int(quantity),
                    ", ".join(selected_toppings) if selected_toppings else "ไม่มี",
                    service_type,
                    payment_type,
                    order_note if order_note else "-",
                    int(total_item_price)
                ]
                # ยิงข้อมูลพิมพ์ต่อท้ายแถวสุดท้ายบน Google Sheets ทันที
                worksheet.append_row(new_row)
                st.success("🎉 บันทึกข้อมูลและซิงค์ไปที่ Google Sheets สำเร็จ!")
                st.rerun()
            else:
                st.error("ไม่สามารถบันทึกได้เนื่องจากระบบเชื่อมต่อฐานข้อมูลไม่สำเร็จ")

with tab2:
    st.subheader("📈 หน้าสรุปยอดปัจจุบัน (ดึงแบบเรียลไทม์)")
    if df_existing.empty:
        st.info("ยังไม่มีข้อมูลออเดอร์ในระบบคลาวด์")
    else:
        st.dataframe(df_existing, use_container_width=True)
        total = pd.to_numeric(df_existing["ราคา"], errors='coerce').sum()
        st.markdown(f"## 🎉 รายรับรวมทั้งหมดในระบบ: `{total:,.2f}` ฿")

with tab3:
    st.subheader("📦 เช็คสต็อกของในร้าน")
    current_selected = []
    for item in STOCK_ITEMS:
        if st.checkbox(f"❌ ต้องซื้อ: **{item}**", key=f"stock_{item}"):
            current_selected.append(item)
    st.session_state.need_to_buy = current_selected
    if st.button("📋 พิมพ์ข้อความรายงานสต็อกด่วนเพื่อส่ง Line"):
        st.code(f"ของที่ต้องซื้อเพิ่มด่วน:\n{', '.join(st.session_state.need_to_buy)}")
