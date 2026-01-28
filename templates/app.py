import os
from flask import Flask, render_template, request
import telebot
from threading import Thread

app = Flask(__name__)

# --- הגדרות ---
TOKEN = "8385525865:AAEgxmw8Sufo35fzEpVT50VFtP4wvhAN3pc"  # <--- הטוקן מה-BotFather
ADMIN_ID =  6504579711  # <--- תחליף את זה ב-ID שלך בטלגרם כדי שרק אתה תוכל להטעין כסף
bot = telebot.TeleBot(TOKEN)

# מסד נתונים זמני (מתאפס כשהשרת נכבה, בהמשך נלמד לשמור לקובץ)
users_db = {}

# --- חלק 1: האתר (Flask) ---
@app.route('/')
def home():
    user_id = request.args.get('id')
    # אם המשתמש לא רשום בבוט, הוא יראה 0
    user = users_db.get(user_id, {"name": "אורח", "balance": "0"})
    return render_template('index.html', user=user)

# --- חלק 2: הבוט (Telegram) ---

# פקודת התחלה
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    
    # רישום משתמש חדש עם 0 שקלים (בלי מתנות חינם!)
    if user_id not in users_db:
        users_db[user_id] = {"name": user_name, "balance": "0"}

    markup = telebot.types.InlineKeyboardMarkup()
    
    # הקישור האמיתי שלך מ-Render
    site_url = f"https://empire-casino.onrender.com/?id={user_id}"
    web_app = telebot.types.WebAppInfo(url=site_url)
    
    btn = telebot.types.InlineKeyboardButton(text="🏰 כניסה ל-EMPIRE STAKES", web_app=web_app)
    markup.add(btn)
    
    bot.reply_to(message, f"שלום {user_name}, ברוך הבא.\nהיתרה שלך מעודכנת באתר.", reply_markup=markup)

# פקודת ניהול להטענת כסף (רק אתה יכול להשתמש בזה)
# כותבים בבוט: /set 123456 500 (ה-ID של המשתמש ואז הסכום)
@bot.message_handler(commands=['set'])
def set_balance(message):
    if message.from_user.id == ADMIN_ID:
        try:
            _, target_id, amount = message.text.split()
            if target_id in users_db:
                users_db[target_id]['balance'] = amount
                bot.reply_to(message, f"✅ היתרה של {users_db[target_id]['name']} עודכנה ל-₪{amount}")
            else:
                bot.reply_to(message, "❌ משתמש לא נמצא במערכת")
        except:
            bot.reply_to(message, "שימוש לא נכון. כתוב: /set [ID] [סכום]")
    else:
        bot.reply_to(message, "אין לך הרשאה לנהל כספים.")

# --- הרצה ---
def run_flask():
    # ב-Render הפורט נקבע אוטומטית
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    # מריץ את האתר בנפרד
    Thread(target=run_flask).start()
    print("--- המערכת באוויר! ---")
    bot.polling(none_stop=True)