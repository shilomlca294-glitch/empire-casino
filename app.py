import os
import telebot
from flask import Flask, render_template, request
from threading import Thread

app = Flask(__name__)

# --- הגדרות ---
# שים לב להחליף את הטוקן ואת ה-ID שלך!
TOKEN = "8385525865:AAEgxmw8Sufo35fzEpVT50VFtP4wvhAN3pc" 
ADMIN_ID = 6504579711 # <--- תחליף למספר שקיבלת מ-userinfobot

bot = telebot.TeleBot(TOKEN)
users_db = {}

# --- חלק 1: האתר (Flask) ---
@app.route('/')
def home():
    user_id = request.args.get('id')
    user = users_db.get(user_id, {"name": "אורח", "balance": "0"})
    return render_template('index.html', user=user)

# --- חלק 2: הבוט (Telegram) ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    
    if user_id not in users_db:
        users_db[user_id] = {"name": user_name, "balance": "0"}

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🏰 כניסה למשחקים", "💰 הפקדה / משיכה")
    markup.add("👤 ניהול חשבון", "💎 שירות לקוחות VIP")
    
    bot.reply_to(message, f"ברוך הבא {user_name} ל-EMPIRE STAKES!", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    user_id = str(message.from_user.id)
    
    if message.text == "🏰 כניסה למשחקים":
        site_url = f"https://empire-casino.onrender.com/?id={user_id}"
        web_app = telebot.types.WebAppInfo(url=site_url)
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton(text="לחץ כאן לכניסה", web_app=web_app)
        markup.add(btn)
        bot.send_message(message.chat.id, "פתח את הקזינו:", reply_markup=markup)

    elif message.text == "💰 הפקדה / משיכה":
        bot.send_message(message.chat.id, "להפקדה, שלח הודעה למנהל:\n@YourUsername")
        bot.send_message(ADMIN_ID, f"🔔 בקשת הפקדה מ: {message.from_user.first_name} (ID: {user_id})")

    elif message.text == "👤 ניהול חשבון":
        user_info = users_db.get(user_id, {"name": "לא רשום", "balance": "0"})
        msg = f"👤 **פרטי חשבון**\n\nשם: {user_info['name']}\nID: `{user_id}`\nיתרה: ₪{user_info['balance']}"
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")

    elif message.text == "💎 שירות לקוחות VIP":
        bot.send_message(message.chat.id, "מוקד ה-VIP זמין עבורך.")

# --- פקודת מנהל להטענת כסף ---
@bot.message_handler(commands=['set'])
def set_balance(message):
    if message.from_user.id == ADMIN_ID:
        try:
            parts = message.text.split()
            if len(parts) == 3:
                target_id = parts[1]
                amount = parts[2]
                if target_id in users_db:
                    users_db[target_id]['balance'] = amount
                    bot.reply_to(message, f"✅ היתרה של {users_db[target_id]['name']} עודכנה ל-₪{amount}")
                else:
                    bot.reply_to(message, "❌ המשתמש לא נמצא במערכת (הוא חייב ללחוץ /start)")
            else:
                bot.reply_to(message, "השתמש בפורמט: /set [ID] [סכום]")
        except Exception as e:
            bot.reply_to(message, f"שגיאה: {e}")
    else:
        bot.reply_to(message, f"אין לך הרשאה. ה-ID שלך הוא: {message.from_user.id}")

# --- הרצה ---
def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    print("--- הבוט והאתר באוויר! ---")
    bot.polling(none_stop=True)

import telebot
import threading
from flask import Flask, render_template_string

# הגדרות בסיסיות
TOKEN = 'כאן_שים_את_הטוקן_שלך'
ADMIN_ID = 12345678 # כאן שים את ה-ID שלך
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# מסד נתונים זמני
users_db = {}

# --- קוד הבוט ---

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    if user_id not in users_db:
        users_db[user_id] = 0
    bot.reply_to(message, f"ברוך הבא לקזינו! ה-ID שלך הוא: {user_id}")

@bot.message_handler(commands=['set'])
def set_balance(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "אין לך הרשאה!")
        return
    
    try:
        parts = message.text.split()
        target_id = parts[1]
        amount = int(parts[2])
        users_db[target_id] = amount
        bot.reply_to(message, f"✅ היתרה של {target_id} עודכנה ל-₪{amount}")
    except:
        bot.reply_to(message, "טעות בפורמט! רשום: /set ID סכום")

# --- קוד האתר ---

@app.route('/')
def home():
    # מציג את כל המשתמשים והיתרות שלהם בדף פשוט
    return f"<h1>Empire Stakes Casino</h1><p>Database: {str(users_db)}</p>"

# --- הרצה משולבת ---

def run_bot():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    # מפעיל את הבוט בנפרד כדי שלא יתקע את האתר
    threading.Thread(target=run_bot).start()
    # מפעיל את האתר
    app.run(host='0.0.0.0', port=10000)
