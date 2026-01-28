import telebot
from telebot import types
import threading
from flask import Flask

# --- הגדרות ---
TOKEN = '8385525865:AAEgxmw8Sufo35fzEpVT50VFtP4wvhAN3pc'
ADMIN_ID = 6504579711  # ה-ID שלך
URL_SITE = "https://your-site.onrender.com" # הקישור לאתר שלך ב-Render
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

users_db = {} # בגרסה הבאה נוסיף שמירה לקובץ

# פונקציה ליצירת המקלדת הראשית
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("🎰 כניסה למשחקים")
    item2 = types.KeyboardButton("👤 ניהול חשבון")
    item3 = types.KeyboardButton("💰 הפקדה / משיכה")
    markup.add(item1)
    markup.add(item2, item3)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    if uid not in users_db:
        users_db[uid] = 0
    bot.send_message(message.chat.id, "ברוך הבא ל-EMPIRE STAKES! 🏆", reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    uid = str(message.from_user.id)
    
    if message.text == "🎰 כניסה למשחקים":
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("לחץ כאן לכניסה לאתר 🌐", url=URL_SITE)
        markup.add(btn)
        bot.send_message(message.chat.id, "בהצלחה במשחקים! לחץ על הכפתור למטה:", reply_markup=markup)

    elif message.text == "👤 ניהול חשבון":
        balance = users_db.get(uid, 0)
        bot.send_message(message.chat.id, f"📋 פרטי חשבון:\n🆔 מזהה: {uid}\n💵 יתרה: ₪{balance}")

    elif message.text == "💰 הפקדה / משיכה":
        bot.send_message(message.chat.id, "להפקדה או משיכה, שלח הודעה למנהל: @YourUsername")

# פקודת ההטענה שלך (נשארת אותו דבר)
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

# --- הרצת האתר ---
@app.route('/')
def home():
    return "<h1>The Casino Site is Running!</h1>"

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=10000)
