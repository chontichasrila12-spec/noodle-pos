import streamlit as st
import pandas as pd
import datetime
import gspread
from google.oauth2.service_account import Credentials

# ตั้งค่าหน้าตาของแอป
st.set_page_config(page_title="ระบบจดออเดอร์ร้านก๋วยจั๊บ", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    h1, h2, h3 { color: #212529; font-family: 'Helvetica Neue', sans-serif; }
    .stButton>button { background-color: #212529; color: white; border-radius: 5px; width: 100%; }
    .stButton>button:hover { background-color: #495057; color: white; }
    </style>
""", unsafe_allow_html=True)

# ฟังก์ชันเชื่อมต่อ Google Sheets แบบเสถียร
def get_google_sheet():
    try:
        # ดึงลิงก์จาก Secrets
        sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        
        # ใช้สิทธิ์การเข้าถึงแบบเปิดสาธารณะที่แชร์ไว้ในการอ่าน/เขียนข้อมูล
        gc = gspread.public(sheet_url)
        # ดึงหน้าชีตชื่อ orders
        worksheet = gc.worksheet("orders")
        return worksheet
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อฐานข้อมูล: {e}")
        return None

worksheet = get_google_sheet()

# โหลดข้อมูลที่มีอยู่เดิมมาแสดงผลสถิติ
if worksheet:
    try:
        data = worksheet.get_all_records()
        df_existing = pd.DataFrame(data)
    except:
        df_existing = pd.DataFrame(columns=["วันที่", "เวลา", "เมนู", "จำนวน", "ท็อปปิ้ง", "รูปแบบ", "การชำระเงิน", "โน้ต", "ราคา"])
else:
    df_existing = pd.DataFrame(columns=["วันที่", "เวลา", "เมนู", "จำนวน", "ท็อปปิ้ง", "รูปแบบ", "การชำระเงิน", "โน้ต", "ราคา"])

# คลังข้อมูลเมนู
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
if 'stock_notes' not in st.session_state: st.session_state.stock_notes = ""

st.title("🍜 ระบบจัดการร้านก๋วยจั๊บ (ระบบสำรองออนไลน์)")
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
        order_note = st.text_input("โน้ตเพิ่มเติม:", "")
    with col2:
        service_type = st.radio("รูปแบบการเสิร์ฟ:", ["ทานที่ร้าน", "กลับบ้าน"])
        payment_type = st.radio("ช่องทางการชำระเงิน:", ["เงินสด", "เงินโอน", "ไทยช่วยไทย", "แกร้ป"])
        
        total_item_price = (base_price + topping_price) * quantity
        if payment_type == "แกร้ป":
            total_item_price = st.number_input("ระบุราคา Grab สุทธิ (บาท):", min_value=0, value=int(total_item_price))
            
        st.markdown(f"### ราคารวม: `{total_item_price}` บาท")
        
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
                # ส่งข้อมูลต่อท้ายตารางไปยัง Google Sheets โดยตรง ไม่ต้องสั่ง update ทับทั่งแผ่น
                worksheet.append_row(new_row)
                st.success("🎉 บันทึกออเดอร์และซิงค์ข้อมูลลง Google Sheets สำเร็จ!")
                st.rerun()
            else:
                st.error("ไม่สามารถบันทึกได้เนื่องจากระบบเชื่อมต่อฐานข้อมูลปลายทางไม่สำเร็จ")

with tab2:
    st.subheader("📈 หน้าสรุปยอดปัจจุบัน")
    if df_existing.empty:
        st.info("ไม่มีข้อมูลในระบบ หรือกำลังโหลดข้อมูล...")
    else:
        st.dataframe(df_existing, use_container_width=True)
        total = pd.to_numeric(df_existing["ราคา"], errors='coerce').sum()
        st.markdown(f"## 🎉 รายรับรวมทั้งหมดในระบบชีต: `{total:,.2f}` ฿")

with tab3:
    st.subheader("📦 เช็คสต็อกของในร้าน")
    current_selected = []
    for item in STOCK_ITEMS:
        if st.checkbox(f"❌ ต้องซื้อ: **{item}**", key=f"stock_{item}"):
            current_selected.append(item)
    st.session_state.need_to_buy = current_selected
    if st.button("📋 พิมพ์ข้อความรายงานสต็อก"):
        st.code(f"ของที่ต้องซื้อเพิ่ม: {', '.join(st.session_state.need_to_buy)}")
TOPPINGS = {
    "พิเศษ": 10, "ไข่": 10, "หมูเด้ง": 10, "หมูสับ": 10, "หมูยอ": 10,
    "กุ้ง": 10, "หมึก": 10, "ปูอัด": 10, "เล้ง": 10, "น่อง": 10,
    "ตีนไก่": 10, "เลือด": 5, "สาหร่าย": 5, "หอมเจียว": 5, "เส้น": 5
}

STOCK_ITEMS = [
    "เลือด", "เส้น", "หมูสับ", "กุ้ง", "หมูยอ", "หมึก", "หมูเด้ง", "สาหร่าย", "ไข่", "น้ำมะนาว",
    "นมเล้ง", "ตีนไก่", "น่องไก่", "หอมเจียว", "ผักชี", "น้ำยาล้างจาน", "น้ำซุป", "พริกซอง",
    "น้ำส้มซอง", "น้ำปลา", "น้ำส้ม", "พริกเผา", "พริกผัด", "พริก", "ถั่ว", "ตะเกียบ", "น้ำตาล",
    "ถุงใส่ซุป", "ถุงหิ้วเล็ก", "ถุงหิ้วใหญ่", "ถุงใส่ก๋วยจั๊บ", "ถุงใส่พริกผัด", "พริกไทย", "มาม่า"
]

if 'need_to_buy' not in st.session_state:
    st.session_state.need_to_buy = []
if 'stock_notes' not in st.session_state:
    st.session_state.stock_notes = ""

st.title("🍜 ระบบจัดการร้านก๋วยจั๊บ (ซิงค์ฐานข้อมูลออนไลน์)")
st.caption(f"วันที่ใช้งาน: {datetime.date.today().strftime('%d/%m/%Y')}")

tab1, tab2, tab3 = st.tabs(["🛒 รับออเดอร์ใหม่", "📊 สรุปยอดและสถิติ", "📦 เช็คสต็อกของในร้าน"])

with tab1:
    st.subheader("เพิ่มรายการอาหาร")
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_menu = st.selectbox("เลือกเมนูหลัก:", list(MENU.keys()))
        base_price = MENU[selected_menu]
        st.write(f"ราคาเริ่มต้น (หน้าร้าน): **{base_price} บาท**")
        selected_toppings = st.multiselect("เพิ่มท็อปปิ้ง:", list(TOPPINGS.keys()))
        topping_price = sum([TOPPINGS[tp] for tp in selected_toppings])
        
        quantity = st.number_input("จำนวน (ชาม):", min_value=1, value=1, step=1)
        order_note = st.text_input("โน้ตเพิ่มเติม (เช่น ไม่เจียว, เผ็ดน้อย):", "")
    with col2:
        service_type = st.radio("รูปแบบการเสิร์ฟ:", ["ทานที่ร้าน", "กลับบ้าน"])
        payment_type = st.radio("ช่องทางการชำระเงิน:", ["เงินสด", "เงินโอน", "ไทยช่วยไทย", "แกร้ป"])
        
        single_price = base_price + topping_price
        standard_total_price = single_price * quantity
        
        if payment_type == "แกร้ป":
            st.warning("🛵 ออเดอร์ Grab: โปรดระบุราคารวมที่ขายจริงในแอป")
            custom_grab_price = st.number_input("ระบุราคา Grab สุทธิ (บาท):", min_value=0, value=int(standard_total_price), step=5)
            total_item_price = int(custom_grab_price)
            st.markdown(f"### ราคารวมออเดอร์แกร้ป: `{total_item_price}` บาท")
        else:
            total_item_price = int(standard_total_price)
            st.markdown(f"### ราคารวมออเดอร์นี้: `{total_item_price}` บาท")
        
        if st.button("➕ บันทึกออเดอร์"):
            new_order = pd.DataFrame([{
                "วันที่": datetime.date.today().strftime("%Y-%m-%d"),
                "เวลา": datetime.datetime.now().strftime("%H:%M:%S"),
                "เมนู": selected_menu,
                "จำนวน": int(quantity),
                "ท็อปปิ้ง": ", ".join(selected_toppings) if selected_toppings else "ไม่มี",
                "รูปแบบ": service_type,
                "การชำระเงิน": payment_type,
                "โน้ต": order_note if order_note else "-",
                "ราคา": int(total_item_price)
            }])
            
            # รวมข้อมูลเก่าและข้อมูลใหม่เข้าด้วยกันแล้วอัปเดตลง Google Sheets
            updated_df = pd.concat([df_existing, new_order], ignore_index=True)
            conn.update(worksheet="orders", data=updated_df)
            st.success(f"บันทึกข้อมูลและซิงค์ไปที่ระบบกลางสำเร็จ! 🎉 ({selected_menu})")
            st.rerun()

with tab2:
    st.subheader("📈 หน้าสรุปยอดและสถิติข้อมูล (ดึงจากฐานข้อมูลกลาง)")
    if df_existing.empty:
        st.info("ยังไม่มีข้อมูลออเดอร์ในระบบคลาวด์")
        total_income = 0
        period_label = "รายวัน"
    else:
        df = df_existing.copy()
        df["วันที่"] = pd.to_datetime(df["วันที่"])
        
        st.markdown("### 🗓️ เลือกช่วงเวลาเพื่อดูสถิติยอดขาย")
        stat_period = st.radio("ตัวเลือกสถิติ:", ["รายวัน (วันนี้)", "รายอาทิตย์ (7 วันย้อนหลัง)", "รายเดือน (30 วันย้อนหลัง)", "รายปี (365 วันย้อนหลัง)"], horizontal=True)
        
        today = pd.Timestamp(datetime.date.today())
        if stat_period == "รายวัน (วันนี้)":
            filtered_df = df[df["วันที่"].dt.date == today.date()]
            period_label = "ประจำวัน"
        elif stat_period == "รายอาทิตย์ (7 วันย้อนหลัง)":
            filtered_df = df[df["วันที่"] >= (today - pd.Timedelta(days=7))]
            period_label = "รายสัปดาห์ (7 วันย้อนหลัง)"
        elif stat_period == "รายเดือน (30 วันย้อนหลัง)":
            filtered_df = df[df["วันที่"] >= (today - pd.Timedelta(days=30))]
            period_label = "รายเดือน (30 วันย้อนหลัง)"
        else:
            filtered_df = df[df["วันที่"] >= (today - pd.Timedelta(days=365))]
            period_label = "รายปี (365 วันย้อนหลัง)"
            
        st.markdown(f"#### 📋 รายการบิลข้อมูล{period_label} (ดับเบิ้ลคลิกแก้ไขตัวเลขในตารางได้ ยอดจะซิงค์ไปหลังบ้านทันที)")
        
        edited_df = st.data_editor(filtered_df, use_container_width=True, num_rows="dynamic")
        
        # ปรับปรุงโครงสร้างข้อมูลหากมีการแก้ไขผ่านหน้าแอป
        if st.button("💾 ยืนยันการอัปเดตข้อมูลแก้ไขบนคลาวด์"):
            for idx, row in edited_df.iterrows():
                orig_indices = df_existing.index[df_existing['เวลา'] == row['เวลา']].tolist()
                if orig_indices:
                    orig_idx = orig_indices[0]
                    df_existing.at[orig_idx, "เมนู"] = row["เมนู"]
                    df_existing.at[orig_idx, "จำนวน"] = row["จำนวน"]
                    df_existing.at[orig_idx, "ราคา"] = row["ราคา"]
                    df_existing.at[orig_idx, "การชำระเงิน"] = row["การชำระเงิน"]
            conn.update(worksheet="orders", data=df_existing)
            st.success("ซิงค์การแก้ไขข้อมูลกลับไปที่ระบบ Google Sheets เรียบร้อยแล้ว!")
            st.rerun()
            
        df = edited_df
        
        st.markdown("---")
        st.markdown("### 🗑️ จัดการลบออเดอร์ที่คีย์ผิดออกจากคลาวด์")
        delete_col1, delete_col2 = st.columns([1, 3])
        with delete_col1:
            row_to_delete = st.number_input("เลือกเลขแถวหน้าสุดที่ต้องการลบ:", min_value=0, max_value=max(0, len(df)-1), step=1, value=0)
        with delete_col2:
            st.write("")
            st.write("") 
            if st.button("❌ ลบออเดอร์แถวนี้ออกจากเซิร์ฟเวอร์") and not df.empty:
                actual_time = df.iloc[int(row_to_delete)]["เวลา"]
                df_existing = df_existing[df_existing["เวลา"] != actual_time]
                conn.update(worksheet="orders", data=df_existing)
                st.success(f"ลบข้อมูลออเดอร์ในระบบคลาวด์เรียบร้อย!")
                st.rerun()
                
        st.markdown("---")
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown(f"### 💰 ยอดรวมแยกประเภท ({period_label})")
            if not df.empty:
                df["ราคา"] = pd.to_numeric(df["ราคา"])
                income_by_pay = df.groupby("การชำระเงิน")["ราคา"].sum().reset_index()
                for index, row in income_by_pay.iterrows():
                    st.write(f"- **{row['การชำระเงิน']}:** {row['ราคา']:.2f} ฿")
                total_income = df["ราคา"].sum()
            else:
                total_income = 0
                st.write("ไม่มีข้อมูลการชำระเงิน")
            st.markdown(f"## 🎉 รายรับรวม{period_label}: `{total_income:,.2f}` ฿")
            
        with c2:
            st.markdown(f"### 🔥 5 อันดับเมนูขายดี ({period_label})")
            if not df.empty:
                top_menus = df["เมนู"].value_counts().head(5)
                for menu_name, count in top_menus.items():
                    st.write(f"🥇 **{menu_name}**: สั่งไปแล้ว {count} ครั้ง")
            else:
                st.write("ยังไม่มีข้อมูลเมนู")
                
        st.markdown("---")
        st.markdown("### 📄 ดาวน์โหลดรายงานสรุปยอดและรายการสต็อกของที่ต้องซื้อ")
        
        summary_text = f"===================================\n   รายงานสรุปข้อมูลร้านก๋วยจั๊บ ({period_label})\n   วันที่ออกเอกสาร: {datetime.date.today().strftime('%d/%m/%Y')}\n===================================\n"
        summary_text += f"รายรับรวมช่วงเวลานี้: {total_income:,.2f} บาท\n-----------------------------------\n"
        
        if not df.empty:
            summary_text += "💰 ยอดรวมแยกตามประเภทการชำระ:\n"
            for index, row in income_by_pay.iterrows():
                summary_text += f"- {row['การชำระเงิน']}: {row['ราคา']} บาท\n"
            
            summary_text += "\n🔥 5 อันดับเมนูขายดี:\n"
            for menu_name, count in top_menus.items():
                summary_text += f"- {menu_name}: {count} ครั้ง\n"
                
            summary_text += "\n📋 รายละเอียดรายการออเดอร์ทั้งหมดในระบบ:\n"
            summary_text += "------------------------------------------------------------------------------------------------------------------------\n"
            summary_text += f"{'วันที่':<12} | {'เวลา':<10} | {'เมนู':<25} | {'จำนวน':<6} | {'ราคา':<8} | {'ชำระเงิน':<12} | {'ท็อปปิ้ง':<25} | {'โน้ต'}\n"
            summary_text += "------------------------------------------------------------------------------------------------------------------------\n"
            for idx, r in df.iterrows():
                date_str = r['วันที่'].strftime('%Y-%m-%d') if isinstance(r['วันที่'], datetime.datetime) else str(r['วันที่'])[:10]
                summary_text += f"{date_str:<12} | {str(r['เวลา']):<10} | {str(r['เมนู']):<25} | {str(r['จำนวน']):<6} | {str(r['ราคา']):<8} | {str(r['การชำระเงิน']):<12} | {str(r['ท็อปปิ้ง']):<25} | {str(r['โน้ต'])}\n"
                
        summary_text += "===================================\n"
        summary_text += "📦 รายการวัตถุดิบและของที่ต้องเบิกซื้อเพิ่ม\n"
        summary_text += "===================================\n"
        if st.session_state.need_to_buy:
            for item in st.session_state.need_to_buy:
                summary_text += f"☑️ ต้องซื้อเพิ่ม: {item}\n"
        else:
            summary_text += "✅ วัตถุดิบทุกอย่างเพียงพอ ไม่ต้องซื้ออะไรเพิ่ม\n"
        summary_text += f"-----------------------------------\n📝 โน้ตสต็อกเพิ่มเติม:\n{st.session_state.stock_notes if st.session_state.stock_notes else '-'}\n"
        summary_text += "==================================="
        
        st.download_button(
            label="💾 ดาวน์โหลดไฟล์สรุปยอดรวมสต็อกและข้อมูลออเดอร์ (Text File)",
            data=summary_text,
            file_name=f"Full_Report_{stat_period}_{datetime.date.today().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )

with tab3:
    st.subheader("📦 เช็คสต็อกของในร้าน (ติ๊กเลือกเฉพาะของที่หมดหรือต้องซื้อเพิ่ม)")
    st.info("💡 คำแนะนำ: เดินดูรอบร้านอันไหนใกล้หมดหรือต้องซื้อเพิ่ม ให้ติ๊กเครื่องหมายถูกหน้าข้อนั้นได้เลยครับ")
    
    sc1, sc2, sc3 = st.columns(3)
    items_per_col = len(STOCK_ITEMS) // 3 + 1
    
    current_selected = []
    for idx, item in enumerate(STOCK_ITEMS):
        is_checked = item in st.session_state.need_to_buy
        if idx < items_per_col:
            with sc1: 
                if st.checkbox(f"❌ ต้องซื้อ: **{item}**", value=is_checked, key=f"chk_{item}"):
                    current_selected.append(item)
        elif idx < items_per_col * 2:
            with sc2: 
                if st.checkbox(f"❌ ต้องซื้อ: **{item}**", value=is_checked, key=f"chk_{item}"):
                    current_selected.append(item)
        else:
            with sc3: 
                if st.checkbox(f"❌ ต้องซื้อ: **{item}**", value=is_checked, key=f"chk_{item}"):
                    current_selected.append(item)
                    
    st.session_state.need_to_buy = current_selected
    
    st.markdown("---")
    st.subheader("📝 โน้ตเพิ่มเติมสำหรับสั่งของ")
    st.session_state.stock_notes = st.text_area("เขียนรายละเอียดเพิ่มเติม (เช่น ยี่ห้อ หรือ จำนวนถุงที่ต้องการฝากซื้อ):", st.session_state.stock_notes)
    
    if st.button("📋 พิมพ์ข้อความรายงานสต็อกด่วนเพื่อส่ง Line"):
        report = f"📋 **รายการสั่งซื้อของเข้าร้านก๋วยจั๊บ ({datetime.date.today().strftime('%d/%m/%Y')})**\n\n"
        if st.session_state.need_to_buy:
            report += "🚨 **ของที่ต้องซื้อเพิ่มด่วน:**\n"
            for i, item in enumerate(st.session_state.need_to_buy, 1):
                report += f"{i}. {item}\n"
        else:
            report += "✅ ของในร้านยังไม่หมด ไม่ต้องซื้ออะไรเพิ่มครับ\n"
        report += f"\n📝 **รายละเอียดเพิ่มเติม:**\n{st.session_state.stock_notes if st.session_state.stock_notes else '-'}"
        
        st.code(report, language="text")
        st.success("เรียบร้อยครับ!")
