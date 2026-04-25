import os
import requests
import pytz
from datetime import datetime
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler

# 1. รับค่า Token และ Chat ID จาก Environment Variables ของ Render
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'ใส่_TOKEN_ของคุณตรงนี้')
CHAT_ID = os.environ.get('CHAT_ID', 'ใส่_CHAT_ID_ของคุณตรงนี้')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', 'ใส่_OPENAI_API_KEY_ของคุณตรงนี้')
RENDER_EXTERNAL_URL = os.environ.get('RENDER_EXTERNAL_URL', '')

app = Flask(__name__)

def get_personal_horoscope():
    """
    ฟังก์ชันสำหรับสร้างคำทำนายดวงเฉพาะบุคคล (ชาย, 26 พ.ค. 2541, ราศีพฤษภ) โดยใช้ OpenAI API
    """
    profile = "ชาย เกิด 26 พ.ค. 2541 (ราศีพฤษภ ♉️)"
    
    # ดึงวันที่ปัจจุบันตามเวลาประเทศไทย
    tz = pytz.timezone('Asia/Bangkok')
    today_date = datetime.now(tz).strftime("%d/%m/%Y")
    
    # ถ้าไม่มี API Key ให้แจ้งเตือน
    if not OPENAI_API_KEY or OPENAI_API_KEY == 'ใส่_OPENAI_API_KEY_ของคุณตรงนี้':
        daily_pred = "⚠️ ยังไม่ได้ตั้งค่า OPENAI_API_KEY ทำให้ไม่สามารถดึงคำทำนายจาก AI ได้ครับ"
    else:
        # เรียกใช้งาน OpenAI API (ChatGPT)
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        prompt = (
            f"เขียนคำทำนายดวงประจำวันที่ {today_date} สำหรับ {profile} "
            "โดยแบ่งเป็น 3 หัวข้อคือ 💼 การงาน, 💰 การเงิน, และ ❤️ ความรัก "
            "ขอให้เนื้อหากระชับ อ่านง่าย ให้กำลังใจ ใช้ภาษาเป็นกันเอง และมีความยาวรวมไม่เกิน 150 คำ"
        )
        
        payload = {
            "model": "gpt-4o-mini", # ใช้รุ่น gpt-4o-mini ที่ฉลาด เร็ว และราคาถูก
            "messages": [
                {"role": "system", "content": "คุณคือหมอดูผู้เชี่ยวชาญด้านโหราศาสตร์ที่ให้คำแนะนำเชิงบวกและแม่นยำ"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        try:
            resp = requests.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            daily_pred = data['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"Error calling OpenAI: {e}")
            daily_pred = "⚠️ เกิดข้อผิดพลาดในการเชื่อมต่อกับ AI ลองใหม่อีกครั้งพรุ่งนี้นะครับ"
    
    # จัดหน้าตาข้อความที่จะส่งเข้า Telegram
    message = f"🔮 **ดวงรายวันของคุณมาแล้ว!** ({today_date})\n"
    message += f"👤 **โปรไฟล์:** {profile}\n"
    message += "━" * 15 + "\n\n"
    message += f"{daily_pred}\n\n"
    message += "━" * 15 + "\n"
    message += "✨ ขอให้วันนี้เป็นวันที่ดีและราบรื่นครับ! ✨"
    
    return message

def send_telegram_message(chat_id=None, text=None):
    """ฟังก์ชันส่งข้อความเข้า Telegram"""
    if text is None:
        text = get_personal_horoscope()
    if chat_id is None:
        chat_id = CHAT_ID

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload)
        tz = pytz.timezone('Asia/Bangkok')
        current_time = datetime.now(tz).strftime("%H:%M:%S")
        if response.status_code == 200:
            print(f"✅ ส่งข้อความเรียบร้อยแล้ว เวลา {current_time}")
        else:
            print(f"❌ เกิดข้อผิดพลาด: {response.text}")
    except Exception as e:
        print(f"❌ ไม่สามารถส่งข้อความได้: {e}")

def setup_bot():
    """ตั้งค่า Webhook และ Menu Button ของบอท"""
    # 1. ตั้งค่าเมนู (Menu Button)
    commands = [
        {"command": "today", "description": "🔮 ดูดวงวันนี้ทันที"},
        {"command": "help", "description": "ℹ️ ข้อมูลการใช้งาน"}
    ]
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/setMyCommands", json={"commands": commands})

    # 2. ตั้งค่า Webhook เพื่อรับข้อความจากผู้ใช้
    if RENDER_EXTERNAL_URL:
        webhook_url = f"{RENDER_EXTERNAL_URL}/webhook"
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook", json={"url": webhook_url})
        print(f"🔗 ตั้งค่า Webhook ไปที่: {webhook_url}")

# รับ Webhook จาก Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    if update and "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")
        
        if text.startswith("/today"):
            # ส่งแจ้งเตือนว่ากำลังสร้างคำทำนาย เนื่องจาก AI อาจจะใช้เวลา 2-3 วินาที
            send_telegram_message(chat_id, "⏳ กำลังให้ AI อ่านไพ่และคำนวณดวงให้ กรุณารอสักครู่นะครับ...")
            send_telegram_message(chat_id) # ส่งดวง
            
        elif text.startswith("/start") or text.startswith("/help"):
            help_msg = "สวัสดีครับ! 🤖 บอทดูดวงส่วนตัวของคุณพร้อมให้บริการ\n\n📌 **การทำงานปกติ:** บอทจะส่งดวงให้ทุกเช้าเวลา 04:30 น.\n🔮 **สั่งงานด้วยตัวเอง:** สามารถกดเมนูซ้ายล่าง หรือพิมพ์ /today เพื่อขอดูดวง ณ ตอนนี้ได้เลยครับ!"
            send_telegram_message(chat_id, help_msg)
            
    return "OK", 200

# สร้าง Route เพื่อให้ UptimeRobot ใช้ Ping เช็คว่าบอทยังทำงานอยู่
@app.route('/')
def keep_alive():
    return "Bot is awake and running! Webhook is active."

# เริ่มต้น Scheduler นอก if __name__ เพื่อให้รองรับการรันผ่าน gunicorn
tz = pytz.timezone('Asia/Bangkok')
scheduler = BackgroundScheduler(timezone=tz)
scheduler.add_job(send_telegram_message, 'cron', hour=4, minute=30)
scheduler.start()

# ตั้งค่า Webhook และ Menu Button ทันทีเมื่อเซิร์ฟเวอร์เริ่มทำงาน
try:
    setup_bot()
except Exception as e:
    print(f"Error setting up bot: {e}")

if __name__ == '__main__':
    print("🤖 บอทดูดวงส่วนตัว กำลังเริ่มต้นทำงาน...")
    
    # รันเว็บเซิร์ฟเวอร์บนพอร์ตที่ Render กำหนด
    port = int(os.environ.get('PORT', 8080))
    # ปิด reloader เพื่อป้องกันไม่ให้รัน Scheduler ซ้ำซ้อน 2 รอบ
    app.run(host='0.0.0.0', port=port, use_reloader=False)
