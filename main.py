import os
import requests
import random
import pytz
from datetime import datetime
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler

BOT_TOKEN = os.environ.get('BOT_TOKEN', 'ใส่_TOKEN_ของคุณตรงนี้')
CHAT_ID = os.environ.get('CHAT_ID', 'ใส่_CHAT_ID_ของคุณตรงนี้')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', 'ใส่_OPENAI_API_KEY_ของคุณตรงนี้')
RENDER_EXTERNAL_URL = os.environ.get('RENDER_EXTERNAL_URL', '')

app = Flask(__name__)

# ==========================================
# ฟังก์ชันเชื่อมต่อ OpenAI (ใช้งานร่วมกัน)
# ==========================================
def call_openai_api(prompt, system_prompt="คุณคือหมอดูผู้เชี่ยวชาญด้านโหราศาสตร์และไพ่ยิปซี ที่ให้คำแนะนำเชิงบวกและแม่นยำ"):
    if not OPENAI_API_KEY or OPENAI_API_KEY == 'ใส่_OPENAI_API_KEY_ของคุณตรงนี้':
        return "⚠️ ยังไม่ได้ตั้งค่า OPENAI_API_KEY ทำให้ไม่สามารถดึงคำทำนายจาก AI ได้ครับ"
    
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    try:
        resp = requests.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        return "⚠️ เกิดข้อผิดพลาดในการเชื่อมต่อกับ AI ลองใหม่อีกครั้งนะครับ"

# ==========================================
# 1. ฟังก์ชันดูดวงประจำวัน (ดวง + สีมงคล + เลขมงคล)
# ==========================================
def get_personal_horoscope():
    profile = "ชาย เกิด 26 พ.ค. 2541 (ราศีพฤษภ ♉️)"
    tz = pytz.timezone('Asia/Bangkok')
    today_date = datetime.now(tz).strftime("%d/%m/%Y")
    
    prompt = (
        f"เขียนคำทำนายดวงประจำวันที่ {today_date} สำหรับ {profile} "
        "โดยแบ่งเป็น 3 หัวข้อคือ 💼 การงาน, 💰 การเงิน, และ ❤️ ความรัก "
        "และส่วนท้ายสุดให้ระบุ 👕 สีเสื้อเสริมดวง (สีมงคล), สีกาลกิณี(ห้ามใส่) และ 🔢 เลขมงคลประจำวัน "
        "ขอให้เนื้อหากระชับ อ่านง่าย ให้กำลังใจ ใช้ภาษาเป็นกันเอง และมีความยาวรวมไม่เกิน 200 คำ"
    )
    
    daily_pred = call_openai_api(prompt)
    
    message = f"🔮 **ดวงรายวันของคุณมาแล้ว!** ({today_date})\n"
    message += f"👤 **โปรไฟล์:** {profile}\n"
    message += "━" * 15 + "\n\n"
    message += f"{daily_pred}\n\n"
    message += "━" * 15 + "\n"
    message += "✨ ขอให้วันนี้เป็นวันที่ดีและราบรื่นครับ! ✨"
    
    return message

# ==========================================
# 2. ฟังก์ชันสุ่มไพ่ยิปซี (Tarot)
# ==========================================
def get_tarot_reading():
    major_arcana = [
        "The Fool (คนโง่/การเริ่มต้นใหม่)", "The Magician (ผู้วิเศษ)", "The High Priestess (นักบวชหญิง)", 
        "The Empress (จักรพรรดินี)", "The Emperor (จักรพรรดิ)", "The Hierophant (พระสังฆราช)", 
        "The Lovers (คู่รัก)", "The Chariot (อัศวินรถม้า)", "Strength (ความเข้มแข็ง)", 
        "The Hermit (ฤาษี)", "Wheel of Fortune (กงล้อแห่งโชคชะตา)", "Justice (ความยุติธรรม)", 
        "The Hanged Man (คนแขวนหัว)", "Death (ความตาย/การเปลี่ยนแปลง)", "Temperance (การย้าย/สมดุล)", 
        "The Devil (ปีศาจ/กิเลส)", "The Tower (หอคอยถล่ม)", "The Star (ดวงดาว/ความหวัง)", 
        "The Moon (พระจันทร์/ความกังวล)", "The Sun (พระอาทิตย์/ความสำเร็จ)", 
        "Judgement (การพิพากษา)", "The World (โลก/ความสมบูรณ์)"
    ]
    card = random.choice(major_arcana)
    profile = "ชาย เกิด 26 พ.ค. 2541 (ราศีพฤษภ ♉️)"
    
    prompt = (
        f"ผู้ใช้โปรไฟล์ {profile} ได้ทำการสุ่มหยิบไพ่ยิปซี 1 ใบ และได้ไพ่ **{card}** "
        f"ช่วยทำนายความหมายของไพ่ใบนี้สำหรับสถานการณ์ปัจจุบันของเขาหน่อย ว่าไพ่กำลังจะบอกหรือเตือนอะไรในวันนี้ "
        "โดยส่วนแรกสุดให้ฟันธงระดับความหมายของไพ่ใบนี้ว่าเป็น '🌟 เกณฑ์: ไพ่ดี', '⚠️ เกณฑ์: ไพ่ระวัง (ไม่ดี)', หรือ '⚖️ เกณฑ์: ไพ่ปานกลาง' "
        "แล้วตามด้วยคำทำนายที่กระชับ เข้าใจง่าย และให้ข้อคิดประจำวัน"
    )
    
    reading = call_openai_api(prompt)
    message = f"🎴 **สุ่มไพ่ยิปซีประจำวัน**\nคุณหยิบได้ไพ่: **{card}**\n"
    message += "━" * 15 + "\n\n" + reading
    return message

# ==========================================
# 3. ฟังก์ชันถาม-ตอบปัญหา (Ask)
# ==========================================
def ask_question(question):
    profile = "ชาย เกิด 26 พ.ค. 2541 (ราศีพฤษภ ♉️)"
    prompt = (
        f"ผู้ใช้โปรไฟล์ {profile} มีคำถามที่อยากปรึกษาคือ: '{question}' "
        "ช่วยให้คำแนะนำตามหลักโหราศาสตร์ ไพ่ยิปซี หรือจิตวิทยาเชิงบวก "
        "ตอบแบบเป็นกันเอง ให้กำลังใจ และมีเหตุผลรองรับ"
    )
    answer = call_openai_api(prompt)
    message = f"💬 **คำถาม:** {question}\n\n**คำแนะนำจาก AI:**\n{answer}"
    return message

# ==========================================
# 4. ฟังก์ชันขอเลขเด็ดหวย (Lotto)
# ==========================================
def get_lotto_prediction(lotto_type):
    profile = "ชาย เกิด 26 พ.ค. 2541 (ราศีพฤษภ ♉️)"
    tz = pytz.timezone('Asia/Bangkok')
    
    # ดึงวันที่และชื่อวัน
    now = datetime.now(tz)
    days_th = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    day_name = days_th[now.weekday()]
    today_date = f"วัน{day_name}ที่ {now.strftime('%d/%m/%Y')}"
    
    prompt = (
        f"ผู้ใช้โปรไฟล์ {profile} ต้องการขอแนวทางเลขเด็ดสำหรับ '{lotto_type}' ประจำ{today_date} "
        "ช่วยวิเคราะห์สถิติ โหราศาสตร์ และให้เลขมงคล (เช่น เลขท้าย 2 ตัว และ 3 ตัว) แบบกระชับ ตรงไปตรงมา "
        "ขอให้มีข้อความอวยพรให้โชคดีถูกรางวัลด้วย"
    )
    answer = call_openai_api(prompt)
    message = f"🎰 **แนวทาง{lotto_type}** ({today_date})\n\n{answer}"
    return message

# ==========================================
# 5. ฤกษ์มงคลประจำวัน (Luck)
# ==========================================
def get_lucky_time():
    profile = "ชาย เกิด 26 พ.ค. 2541 (ราศีพฤษภ ♉️)"
    tz = pytz.timezone('Asia/Bangkok')
    now = datetime.now(tz)
    days_th = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    day_name = days_th[now.weekday()]
    today_date = f"วัน{day_name}ที่ {now.strftime('%d/%m/%Y')}"
    prompt = (
        f"วิเคราะห์ฤกษ์มงคลประจำ{today_date} สำหรับ {profile} "
        "โดยระบุ ⏰ ช่วงเวลาฤกษ์ดี (เหมาะทำเรื่องสำคัญ เช่น เซ็นสัญญา เจรจา เริ่มงานใหม่) "
        "และ ⛔ ช่วงเวลาที่ควรระวัง พร้อมคำแนะนำสั้นๆ กระชับ"
    )
    answer = call_openai_api(prompt)
    return f"📅 **ฤกษ์มงคลประจำวัน** ({today_date})\n━━━━━━━━━━━━━━━\n\n{answer}"

# ==========================================
# 6. เช็คดวงคู่ครอง (Match)
# ==========================================
def get_match_reading(partner_info):
    profile = "ชาย เกิด 26 พ.ค. 2541 (ราศีพฤษภ ♉️)"
    prompt = (
        f"วิเคราะห์ความเข้ากันได้ระหว่าง {profile} กับคนที่เกิด '{partner_info}' "
        "โดยให้คะแนนความเข้ากัน (%) และวิเคราะห์ด้านความรัก การใช้ชีวิตร่วมกัน "
        "จุดแข็ง จุดที่ควรระวัง และคำแนะนำสำหรับคู่นี้ เขียนกระชับเป็นกันเอง"
    )
    answer = call_openai_api(prompt)
    return f"💞 **เช็คดวงคู่ครอง**\n👤 คุณ: {profile}\n💕 คู่ของคุณ: {partner_info}\n━━━━━━━━━━━━━━━\n\n{answer}"

# ==========================================
# 7. คำคมบำบัดใจ (Quote)
# ==========================================
def get_daily_quote():
    prompt = (
        "สุ่มสร้างคำคมมงคลหรือข้อคิดดีๆ ให้กำลังใจ 1 ข้อความ "
        "อาจเป็นคำสอนจากปราชญ์ หลักธรรม หรือข้อคิดจากประสบการณ์ชีวิต "
        "เขียนสั้นๆ กระชับ 1-3 บรรทัด ภาษาไทยเข้าใจง่าย ให้พลังบวก"
    )
    answer = call_openai_api(prompt)
    return f"🧘 **คำคมบำบัดใจประจำวัน**\n━━━━━━━━━━━━━━━\n\n{answer}\n\n✨ ขอให้มีความสุขในทุกๆ วันครับ ✨"

# ==========================================
# ระบบส่งข้อความ Telegram
# ==========================================
def send_telegram_message(chat_id=None, text=None, reply_markup=None, use_accept_buttons=False):
    if text is None:
        text = get_personal_horoscope()
        # ไม่ใช้ปุ่มตอบรับสำหรับดวงตอนเช้า
    if chat_id is None:
        chat_id = CHAT_ID

    if use_accept_buttons and reply_markup is None:
        reply_markup = {
            "inline_keyboard": [
                [
                    {"text": "🙏 น้อมรับคำทำนาย", "callback_data": "accept_pred"},
                    {"text": "🙅‍♂️ ไม่รับคำทำนาย", "callback_data": "reject_pred"}
                ]
            ]
        }

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
        
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"❌ ไม่สามารถส่งข้อความได้: {e}")

# ==========================================
# การตั้งค่า Webhook และ Menu Button
# ==========================================
def setup_bot():
    commands = [
        {"command": "today", "description": "🔮 ดูดวงวันนี้ (สีมงคล/เลขมงคล)"},
        {"command": "tarot", "description": "🎴 สุ่มเปิดไพ่ยิปซี 1 ใบ"},
        {"command": "lotto", "description": "🎰 ขอเลขเด็ด (หวยไทย/หวยลาว)"},
        {"command": "luck", "description": "📅 ฤกษ์มงคลประจำวัน"},
        {"command": "match", "description": "💞 เช็คดวงคู่ครอง (/match วันเกิด)"},
        {"command": "quote", "description": "🧘 คำคมบำบัดใจ"},
        {"command": "ask", "description": "💬 ถามปัญหาชีวิต (/ask คำถาม)"},
        {"command": "help", "description": "ℹ️ ข้อมูลการใช้งาน"}
    ]
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/setMyCommands", json={"commands": commands})

    if RENDER_EXTERNAL_URL:
        webhook_url = f"{RENDER_EXTERNAL_URL}/webhook"
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook", json={"url": webhook_url})
        print(f"🔗 ตั้งค่า Webhook ไปที่: {webhook_url}")

# ==========================================
# ส่วนของ Flask Web Server
# ==========================================
@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    
    # 1. จัดการเมื่อผู้ใช้กดปุ่ม (Callback Query) จากการเลือกไพ่ยิปซี
    if update and "callback_query" in update:
        cq = update["callback_query"]
        chat_id = cq["message"]["chat"]["id"]
        data = cq["data"]
        
        if data.startswith("tarot_"):
            # แจ้งให้ Telegram ทราบว่ารับคำสั่งปุ่มแล้ว
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery", json={"callback_query_id": cq["id"]})
            
            # ส่งข้อความรอ
            send_telegram_message(chat_id, "🎴 กำลังหงายไพ่ที่คุณเลือกและตีความความหมาย...")
            # ดึงคำทำนาย พร้อมแนบปุ่มน้อมรับคำทำนาย
            send_telegram_message(chat_id, get_tarot_reading(), use_accept_buttons=True)
            
        elif data.startswith("lotto_"):
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery", json={"callback_query_id": cq["id"]})
            
            lotto_type = "หวยไทย 🇹🇭" if data == "lotto_thai" else "หวยลาว 🇱🇦"
            send_telegram_message(chat_id, f"🎲 กำลังคำนวณสถิติและเลขมงคลสำหรับ {lotto_type} รอสักครู่นะครับ...")
            
            # ส่งเลขเด็ด (ไม่ใช้ปุ่มรับคำทำนาย)
            send_telegram_message(chat_id, get_lotto_prediction(lotto_type))
            
        elif data == "accept_pred":
            # แจ้ง Alert หน้าจอ
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery", json={
                "callback_query_id": cq["id"],
                "text": "🙏 สาธุ ขอให้สิ่งดีๆ สมหวังดังคำทำนายครับ ✨",
                "show_alert": True
            })
            # เปลี่ยนปุ่มเป็นสถานะกดแล้ว
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageReplyMarkup", json={
                "chat_id": chat_id,
                "message_id": cq["message"]["message_id"],
                "reply_markup": {"inline_keyboard": [[{"text": "✅ น้อมรับคำทำนายแล้ว", "callback_data": "done"}]]}
            })
            
        elif data == "reject_pred":
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery", json={
                "callback_query_id": cq["id"],
                "text": "🙅‍♂️ ปัดเป่าสิ่งร้าย! ขอให้แคล้วคลาดปลอดภัยครับ 🛡️",
                "show_alert": True
            })
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageReplyMarkup", json={
                "chat_id": chat_id,
                "message_id": cq["message"]["message_id"],
                "reply_markup": {"inline_keyboard": [[{"text": "❌ ไม่รับคำทำนาย", "callback_data": "done"}]]}
            })
            
        return "OK", 200

    # 2. จัดการเมื่อผู้ใช้พิมพ์ข้อความปกติ
    if update and "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")
        
        if text.startswith("/today"):
            send_telegram_message(chat_id, "⏳ กำลังสแกนดวง และคำนวณสีมงคล/เลขมงคลให้ครับ รอสักครู่...")
            send_telegram_message(chat_id, get_personal_horoscope())
            
        elif text.startswith("/tarot"):
            # สร้างปุ่มให้ผู้ใช้กดเลือกไพ่ 3 ใบ
            keyboard = {
                "inline_keyboard": [
                    [
                        {"text": "🃏 ใบซ้าย", "callback_data": "tarot_left"},
                        {"text": "🃏 ใบกลาง", "callback_data": "tarot_center"},
                        {"text": "🃏 ใบขวา", "callback_data": "tarot_right"}
                    ]
                ]
            }
            send_telegram_message(chat_id, "ตั้งสมาธิ อธิษฐานในใจ แล้วจิ้มเลือกไพ่ 1 ใบเลยครับ 👇", reply_markup=keyboard)
            
        elif text.startswith("/lotto"):
            keyboard = {
                "inline_keyboard": [
                    [
                        {"text": "🇹🇭 หวยไทย", "callback_data": "lotto_thai"},
                        {"text": "🇱🇦 หวยลาว", "callback_data": "lotto_lao"}
                    ]
                ]
            }
            msg = (
                "🎰 **คุณต้องการขอแนวทางเลขเด็ดสำหรับหวยประเภทไหนครับ?**\n\n"
                "🗓️ **กำหนดการออกรางวัล:**\n"
                "🇹🇭 **หวยไทย:** ออกทุกวันที่ 1 และ 16 ของเดือน\n"
                "🇱🇦 **หวยลาว:** ออกรางวัลวันจันทร์-ศุกร์ (5 วัน/สัปดาห์)\n\n"
                "*(ระบบ AI จะคำนวณเลขเด็ดตามดวงดาวและวันเวลาปัจจุบันให้ครับ)* 👇"
            )
            send_telegram_message(chat_id, msg, reply_markup=keyboard)
            
        elif text.startswith("/luck"):
            send_telegram_message(chat_id, "⏳ กำลังคำนวณฤกษ์มงคลให้ครับ...")
            send_telegram_message(chat_id, get_lucky_time())
            
        elif text.startswith("/match"):
            partner = text.replace("/match", "").strip()
            if not partner:
                send_telegram_message(chat_id, "❓ โปรดพิมพ์วันเกิดของคนที่สนใจต่อท้ายด้วยครับ\nเช่น: `/match 14 ก.พ. 2542` หรือ `/match ราศีกันย์`")
            else:
                send_telegram_message(chat_id, f"💞 กำลังวิเคราะห์ดวงคู่ครองให้ รอสักครู่...")
                send_telegram_message(chat_id, get_match_reading(partner))
                
        elif text.startswith("/quote"):
            send_telegram_message(chat_id, "🧘 กำลังเลือกคำคมดีๆ ให้คุณ...")
            send_telegram_message(chat_id, get_daily_quote())
            
        elif text.startswith("/ask"):
            question = text.replace("/ask", "").strip()
            if not question:
                send_telegram_message(chat_id, "❓ โปรดพิมพ์คำถามต่อท้ายคำสั่งด้วยครับ\nเช่น: `/ask วันนี้ควรซื้อหวยเลขอะไรดี?`")
            else:
                send_telegram_message(chat_id, f"🤔 กำลังหาคำตอบสำหรับ: '{question}' ...")
                send_telegram_message(chat_id, ask_question(question))
                
        elif text.startswith("/start") or text.startswith("/help"):
            help_msg = (
                "สวัสดีครับ! 🤖 บอทดูดวงส่วนตัวของคุณพร้อมให้บริการ\n\n"
                "📌 **เมนูคำสั่งทั้งหมด:**\n"
                "🔮 `/today` - ดูดวงรายวัน พร้อมสี/เลขมงคล\n"
                "🎴 `/tarot` - สุ่มเปิดไพ่ยิปซีประจำวัน\n"
                "🎰 `/lotto` - ขอแนวทางเลขเด็ดหวยไทย/ลาว\n"
                "📅 `/luck` - ฤกษ์มงคลประจำวัน\n"
                "💞 `/match [วันเกิด]` - เช็คดวงคู่ครอง\n"
                "🧘 `/quote` - คำคมบำบัดใจ\n"
                "💬 `/ask [คำถาม]` - ปรึกษาปัญหาชีวิต\n\n"
                "*(บอทจะส่งดวงให้แบบอัตโนมัติทุกเช้าเวลา 04:30 น. ด้วยครับ)*"
            )
            send_telegram_message(chat_id, help_msg)
            
    return "OK", 200

@app.route('/')
def keep_alive():
    return "Bot is awake and running! Webhook is active."

# เริ่มต้น Scheduler
tz = pytz.timezone('Asia/Bangkok')
scheduler = BackgroundScheduler(timezone=tz)
scheduler.add_job(send_telegram_message, 'cron', hour=4, minute=30)
scheduler.start()

try:
    setup_bot()
except Exception as e:
    pass

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, use_reloader=False)
