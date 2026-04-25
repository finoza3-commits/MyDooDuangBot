import os
import requests
import random
import pytz
from datetime import datetime
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

# 1. รับค่า Token และ Chat ID จาก Environment Variables ของ Render
# หากรันบนเครื่องตัวเองให้ใส่ Token/Chat ID แทน 'ใส่_TOKEN_ของคุณตรงนี้' ได้เลย
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'ใส่_TOKEN_ของคุณตรงนี้')
CHAT_ID = os.environ.get('CHAT_ID', 'ใส่_CHAT_ID_ของคุณตรงนี้')

app = Flask(__name__)

def get_personal_horoscope():
    """
    ฟังก์ชันสำหรับสร้างคำทำนายดวงเฉพาะบุคคล (ชาย, 26 พ.ค. 2541, ราศีพฤษภ)
    """
    profile = "ชาย เกิด 26 พ.ค. 2541 (ราศีพฤษภ ♉️)"
    
    # ฐานข้อมูลคำทำนายจำลองสำหรับชาวพฤษภ (สุ่มเพื่อไม่ให้ข้อความซ้ำกันทุกวัน)
    predictions = [
        "💼 **การงาน:** วันนี้อาจมีงานที่ต้องใช้ความละเอียดสูง ขอให้ใช้ความใจเย็นและความหนักแน่นของชาวพฤษภจัดการ รับรองว่าผ่านไปได้\n💰 **การเงิน:** มีเกณฑ์เสียเงินกับของอร่อยๆ หรือการให้รางวัลตัวเอง\n❤️ **ความรัก:** คนโสดมีเสน่ห์ดึงดูด คนมีคู่ระวังเรื่องความดื้อเงียบของตัวเอง",
        "💼 **การงาน:** ราบรื่นดี สิ่งที่คิดหรือวางแผนไว้เริ่มเป็นรูปเป็นร่างและเห็นผลชัดเจนขึ้น\n💰 **การเงิน:** ทรงตัว บริหารจัดการได้ดี แต่อย่าเพิ่งลงทุนในสิ่งที่มีความเสี่ยงสูง\n❤️ **ความรัก:** ได้รับกำลังใจจากคนรอบข้างเป็นอย่างดี วันนี้ความสัมพันธ์สงบสุข",
        "💼 **การงาน:** ระวังความขัดแย้งเล็กๆ น้อยๆ กับคนรอบข้าง ค่อยๆ พูดจากันด้วยเหตุผลจะดีที่สุด\n💰 **การเงิน:** มีโอกาสได้โชคลาภเล็กๆ หรือได้ของถูกใจในราคาที่คุ้มค่า\n❤️ **ความรัก:** วันนี้มีเสน่ห์ในแบบฉบับผู้ชายอบอุ่นเป็นพิเศษ ระวังคนเข้ามาพร้อมกันหลายคน",
        "💼 **การงาน:** งานหนักนิดนึง ต้องใช้ความอดทนสูง แต่ผลลัพธ์ที่ได้จากความพยายามจะคุ้มค่ามาก\n💰 **การเงิน:** ระวังการตัดสินใจซื้อของชิ้นใหญ่แบบปุบปับ ควรเช็กราคาเปรียบเทียบให้ดีก่อน\n❤️ **ความรัก:** คนมีคู่ดูแลกันดี คนโสดช่วงนี้อาจอยากโฟกัสเรื่องการสร้างฐานะมากกว่า",
        "💼 **การงาน:** เป็นวันที่ดีสำหรับการลุยโปรเจกต์ใหม่ หรือนำเสนอไอเดียที่คุณคิดมานาน\n💰 **การเงิน:** มีแนวโน้มการหมุนเงินที่คล่องตัวขึ้น อาจมีรายรับพิเศษเข้ามา\n❤️ **ความรัก:** คนรักเอาใจใส่ดูแลดีเป็นพิเศษ คนโสดอาจพบคนถูกใจจากสายงานเดียวกัน"
    ]
    
    # ดึงวันที่ปัจจุบันตามเวลาประเทศไทย
    tz = pytz.timezone('Asia/Bangkok')
    today_date = datetime.now(tz).strftime("%d/%m/%Y")
    
    # สุ่มคำทำนาย 1 รูปแบบ
    daily_pred = random.choice(predictions)
    
    # จัดหน้าตาข้อความที่จะส่งเข้า Telegram
    message = f"🔮 **ดวงรายวันของคุณมาแล้ว!** ({today_date})\n"
    message += f"👤 **โปรไฟล์:** {profile}\n"
    message += "━" * 15 + "\n\n"
    message += f"{daily_pred}\n\n"
    message += "━" * 15 + "\n"
    message += "✨ ขอให้วันนี้เป็นวันที่ดีและราบรื่นครับ! ✨"
    
    return message

def send_telegram_message():
    """ฟังก์ชันส่งข้อความเข้า Telegram"""
    text = get_personal_horoscope()
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload)
        tz = pytz.timezone('Asia/Bangkok')
        current_time = datetime.now(tz).strftime("%H:%M:%S")
        if response.status_code == 200:
            print(f"✅ ส่งดวงราศีพฤษภเรียบร้อยแล้ว เวลา {current_time}")
        else:
            print(f"❌ เกิดข้อผิดพลาด: {response.text}")
    except Exception as e:
        print(f"❌ ไม่สามารถส่งข้อความได้: {e}")

# สร้าง Route เพื่อให้ UptimeRobot ใช้ Ping เช็คว่าบอทยังทำงานอยู่
@app.route('/')
def keep_alive():
    return "Bot is awake and running!"

if __name__ == '__main__':
    print("🤖 บอทดูดวงส่วนตัว (ราศีพฤษภ) กำลังเริ่มต้นทำงาน...")
    
    # ตั้งค่า Scheduler โดยใช้เวลาประเทศไทย (Asia/Bangkok)
    tz = pytz.timezone('Asia/Bangkok')
    scheduler = BackgroundScheduler(timezone=tz)
    
    # 2. ตั้งเวลาที่ต้องการส่ง ในที่นี้คือ 04:30 น. (เช้ามืด) ของทุกวัน
    scheduler.add_job(send_telegram_message, 'cron', hour=4, minute=30)
    scheduler.start()
    
    # รันเว็บเซิร์ฟเวอร์บนพอร์ตที่ Render กำหนด หรือพอร์ต 8080 (สำหรับการทำงานคู่กับ UptimeRobot)
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
