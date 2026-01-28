import telebot
from telebot import types
import threading
from flask import Flask

# --- הגדרות ---
TOKEN = '8385525865:AAEgxmw8Sufo35fzEpVT50VFtP4wvhAN3pc'
ADMIN_ID = 6504579711  # ה-ID שלך
URL_SITE = "https://your-site.onrender.com" # הקישור שלך מרנדר
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

users_db = {} 

# תפריט כפתורים ראשי
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🎰 כניסה למשחקים")
    btn2 = types.KeyboardButton("👤 ניהול חשבון")
    btn3 = types.KeyboardButton("💰 הפקדה / משיכה")
    btn4 = types.KeyboardButton("💎 שירות לקוחות VIP")
    markup.add(btn1)
    markup.add(btn2, btn3)
    markup.add(btn4)
    return markup

# ... (כאן נמצא הקוד של ה-start והגדרות הבוט)

@bot.message_handler(commands=['start'])
def start(message):
    # הקוד של הסטארט...
    pass

# הנה המקום! תדביק את הקוד ששלחת כאן:
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    uid = str(message.from_user.id)
    text = message.text
    print(f"Received message: '{text}' from {uid}")

    if "כניסה למשחקים" in text:
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("לחץ כאן לכניסה לאתר 🌐", url=URL_SITE)
        markup.add(btn)
        bot.send_message(message.chat.id, "בהצלחה! לחץ למטה:", reply_markup=markup)

    elif "שירות לקוחות" in text or "VIP" in text:
        bot.send_message(message.chat.id, "👑 מוקד VIP זמין עבורך! פנה למנהל: @YourUsername")

    elif "ניהול חשבון" in text:
        balance = users_db.get(uid, 0)
        bot.send_message(message.chat.id, f"📋 פרטי חשבון:\n🆔 מזהה: {uid}\n💵 יתרה: ₪{balance}")

    elif "הפקדה" in text:
        bot.send_message(message.chat.id, "💳 להפקדה או משיכה שלח הודעה למנהל.")

# אחרי זה מגיע הקוד של ה-set והרצת השרת...

# פקודת ניהול להטענת כסף
@bot.message_handler(commands=['set'])
def set_balance(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        parts = message.text.split()
        target_id, amount = parts[1], int(parts[2])
        users_db[target_id] = amount
        bot.reply_to(message, f"✅ היתרה של {target_id} עודכנה ל-₪{amount}")
    except:
        bot.reply_to(message, "שימוש: /set ID סכום")

# --- חלק האתר (לרנדר) ---
@app.route('/')
def home():
    return "<h1>The Casino Site is Live</h1>"

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=10000)

