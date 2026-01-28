import telebot
from telebot import types
import threading
import json
import os
from flask import Flask

# ================= הגדרות אישיות - תעדכן כאן! =================
TOKEN = '8385525865:AAEgxmw8Sufo35fzEpVT50VFtP4wvhAN3pc'
ADMIN_ID = 6504579711  # ה-ID שקיבלת מה-userinfobot
URL_SITE = "https://empire-stakes.onrender.com"  # הקישור שלך מרנדר
# ===========================================================

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
DB_FILE = "users_db.json"

# --- ניהול מסד נתונים פשוט בקובץ ---
def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# טעינת המשתמשים לזיכרון
users_db = load_data()

# --- פונקציות עזר לעיצוב ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🎰 כניסה למשחקים"))
    markup.add(types.KeyboardButton("👤 ניהול חשבון"), types.KeyboardButton("💰 הפקדה / משיכה"))
    markup.add(types.KeyboardButton("💎 שירות לקוחות VIP"))
    return markup

# --- פקודות בוט ---

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    if uid not in users_db:
        users_db[uid] = 0
        save_data(users_db)
    
    welcome_text = (
        "🏆 **ברוך הבא ל-EMPIRE STAKES!** 🏆\n\n"
        "כאן תוכל לשחק ברולטה, סלוטים ועוד.\n"
        f"ה-ID שלך במערכת: `{uid}`\n"
        f"היתרה הנוכחית: **₪{users_db[uid]}**"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=main_menu())

@bot.message_handler(commands=['set'])
def set_balance(message):
    # בדיקה אם השולח הוא המנהל
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ פקודה זו מיועדת למנהל בלבד!")
        return

    try:
        # פורמט פקודה: /set 12345678 500
        args = message.text.split()
        target_id = args[1]
        amount = int(args[2])
        
        users_db[target_id] = amount
        save_data(users_db)
        
        bot.send_message(message.chat.id, f"✅ **הצלחה!**\nהיתרה של משתמש `{target_id}` עודכנה ל-**₪{amount}**", parse_mode="Markdown")
        # שליחת הודעה למשתמש המוטען אם הוא קיים
        try:
            bot.send_message(target_id, f"💰 **החשבון שלך הוטען!**\nהיתרה החדשה שלך היא: **₪{amount}**", parse_mode="Markdown")
        except:
            pass
    except Exception as e:
        bot.reply_to(message, "⚠️ **טעות בפורמט!**\nרשום: `/set ID סכום`", parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    uid = str(message.from_user.id)
    text = message.text

    if "כניסה למשחקים" in text:
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("לחץ כאן לכניסה לאתר 🌐", url=URL_SITE)
        markup.add(btn)
        bot.send_message(message.chat.id, "בהצלחה במשחקים! לחץ על הכפתור למטה:", reply_markup=markup)

    elif "ניהול חשבון" in text:
        balance = users_db.get(uid, 0)
        bot.send_message(message.chat.id, f"📋 **פרטי חשבון:**\n🆔 מזהה: `{uid}`\n💵 יתרה: **₪{balance}**", parse_mode="Markdown")

    elif "שירות לקוחות" in text or "VIP" in text:
        bot.send_message(message.chat.id, "💎 **מוקד VIP איתך!**\nלכל שאלה או עזרה, פנה אלינו: @YourAdminUsername")

    elif "הפקדה" in text:
        bot.send_message(message.chat.id, f"💰 **הפקדה / משיכה**\nשלח למנהל את המזהה שלך: `{uid}`\nהמנהל יעדכן לך את היתרה באופן מיידי.")

# --- חלק האתר (Flask) ---

@app.route('/')
def home():
    return """
    <body style="background:#000; color:#d4af37; text-align:center; font-family:sans-serif; padding-top:100px;">
        <h1>EMPIRE STAKES</h1>
        <p>The Casino Server is Live!</p>
        <div style="border:1px solid #d4af37; display:inline-block; padding:20px; border-radius:10px;">
            Go back to the Telegram Bot to play.
        </div>
    </body>
    """

# --- הפעלה משולבת ---

def run_bot():
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    # הרצת הבוט בנפרד
    threading.Thread(target=run_bot).start()
    # הרצת האתר
    app.run(host='0.0.0.0', port=10000)
