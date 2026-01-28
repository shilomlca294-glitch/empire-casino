import telebot
from telebot import types
import threading
from flask import Flask

# --- הגדרות ---
TOKEN = '8385525865:AAEgxmw8Sufo35fzEpVT50VFtP4wvhAN3pc'
ADMIN_ID = 6504579711  # ה-ID שלך
URL_SITE = "https://your-site.onrender.com"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
users_db = {}

# תפריט כפתורים
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🎰 כניסה למשחקים"))
    markup.add(types.KeyboardButton("👤 ניהול חשבון"), types.KeyboardButton("💰 הפקדה / משיכה"))
    markup.add(types.KeyboardButton("💎 שירות לקוחות VIP"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    if uid not in users_db: users_db[uid] = 0
    bot.send_message(message.chat.id, "🏆 EMPIRE STAKES 🏆", reply_markup=main_menu())

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    uid = str(message.from_user.id)
    if "כניסה למשחקים" in message.text:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("לחץ לכניסה 🌐", url=URL_SITE))
        bot.send_message(message.chat.id, "בהצלחה!", reply_markup=markup)
    elif "ניהול חשבון" in message.text:
        bot.send_message(message.chat.id, f"יתרה: ₪{users_db.get(uid, 0)}")

@app.route('/')
def home():
    return "<h1>Empire Stakes is Up!</h1>"

def run_bot():
    # skip_pending=True פותר את בעיית ה-Conflict ברוב המקרים
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=10000)
