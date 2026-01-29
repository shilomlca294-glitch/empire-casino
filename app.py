import telebot
from telebot import types
import threading
import json
import os
from flask import Flask, request

# ================= פרטי המערכת שלך =================
TOKEN = '8385525865:AAEgxmw8Sufo35fzEpVT50VFtP4wvhAN3pc'
ADMIN_ID = 6504579711  # ה-ID שלך - רק אתה שולט בכסף
GROUP_URL = "https://t.me/+W1FOgCfwvKczNDg0" # שים פה קישור לקבוצה שלך
URL_SITE = "https://empire-stakes.onrender.com" # הקישור שלך מרנדר
# ===============================================

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
DB_FILE = "casino_db.json"

# פונקציות מסד נתונים
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f: return json.load(f)
        except: return {}
    return {}

def save_db(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f, indent=4)

users_db = load_db()

# --- פקודות ניהול (טען, הסר, מינוס) - רק למנהל ---

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and any(word in m.text for word in ["טען", "הסר", "מינוס"]))
def admin_commands(message):
    try:
        parts = message.text.split()
        if len(parts) < 3: return
        
        command = parts[0]    # טען / הסר / מינוס
        target_id = parts[1]  # ID של השחקן
        amount = int(parts[2]) # סכום

        if target_id not in users_db:
            bot.reply_to(message, "❌ המשתמש לא נמצא במערכת (הוא חייב ללחוץ /start קודם)")
            return

        if command == "טען":
            users_db[target_id]["balance"] += amount
            users_db[target_id]["total_deposited"] += amount
            res_msg = f"✅ טענתי ₪{amount} למשתמש {target_id}"
            bot.send_message(target_id, f"💰 **חשבונך הוטען!**\nנוספו: ₪{amount}\nיתרה חדשה: ₪{users_db[target_id]['balance']}", parse_mode="Markdown")

        elif command == "הסר":
            users_db[target_id]["balance"] -= amount
            users_db[target_id]["total_withdrawn"] += amount
            res_msg = f"✅ הסרתי ₪{amount} למשתמש {target_id}"
            bot.send_message(target_id, f"💸 **משיכה בוצעה!**\nהוסרו מחשבונך: ₪{amount}\nיתרה חדשה: ₪{users_db[target_id]['balance']}", parse_mode="Markdown")

        elif command == "מינוס":
            users_db[target_id]["balance"] = -amount
            res_msg = f"⚠️ המשתמש {target_id} הוכנס למינוס של ₪{amount}-"
            bot.send_message(target_id, f"⛔ **חשבונך במינוס!**\nיתרה נוכחית: ₪{amount}-", parse_mode="Markdown")

        save_db(users_db)
        bot.reply_to(message, res_msg)
    except Exception as e:
        bot.reply_to(message, "⚠️ פורמט לא תקין! תכתוב למשל: `טען 12345 500`", parse_mode="Markdown")

# --- תפריטים ופונקציות משתמש ---

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🎰 כניסה למשחקים")
    btn2 = types.KeyboardButton("🔗 כניסה לקבוצה")
    btn3 = types.KeyboardButton("💰 הפקדה / משיכה")
    btn4 = types.KeyboardButton("💵 היתרה שלי")
    btn5 = types.KeyboardButton("👤 פרטי שחקן")
    markup.add(btn1)
    markup.add(btn2, btn3)
    markup.add(btn4, btn5)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    if uid not in users_db:
        users_db[uid] = {
            "balance": 0,
            "total_deposited": 0,
            "total_withdrawn": 0,
            "total_lost": 0,
            "favorite_game": "אין"
        }
        save_db(users_db)
    bot.send_message(message.chat.id, "🏆 **ברוך הבא ל-EMPIRE STAKES!**\nבחר באחת האפשרויות:", 
                     parse_mode="Markdown", reply_markup=main_menu())

@bot.message_handler(func=lambda m: True)
def handle_menu(message):
    uid = str(message.from_user.id)
    text = message.text

    if text == "🎰 כניסה למשחקים":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("פתח קזינו 🌐", url=f"{URL_SITE}/?user_id={uid}"))
        bot.send_message(message.chat.id, "🎰 המזל איתך! לחץ על הכפתור כדי להתחיל:", reply_markup=markup)

    elif text == "🔗 כניסה לקבוצה":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("להצטרפות לקבוצה 📢", url=GROUP_URL))
        bot.send_message(message.chat.id, "לחץ למטה כדי להיכנס לקבוצה:", reply_markup=markup)

    elif text == "💰 הפקדה / משיכה":
        bot.send_message(message.chat.id, "📩 בקשתך נשלחה למנהל, הוא ייצור איתך קשר.")
        bot.send_message(ADMIN_ID, f"🔔 **בקשת הפקדה/משיכה!**\nמשתמש: {message.from_user.first_name}\nID: `{uid}`", parse_mode="Markdown")

    elif text == "💵 היתרה שלי":
        balance = users_db.get(uid, {}).get("balance", 0)
        bot.send_message(message.chat.id, f"💰 היתרה שלך: **₪{balance}**", parse_mode="Markdown")

    elif text == "👤 פרטי שחקן":
        u = users_db.get(uid, {})
        stats = (
            f"👤 **כרטיס שחקן VIP**\n\n"
            f"💵 יתרה: **₪{u.get('balance', 0)}**\n"
            f"📥 סך הפקדות: ₪{u.get('total_deposited', 0)}\n"
            f"📤 סך משיכות: ₪{u.get('total_withdrawn', 0)}\n"
            f"📉 סך הפסדים: ₪{u.get('total_lost', 0)}\n"
            f"🎮 משחק מועדף: {u.get('favorite_game', 'אין')}"
        )
        bot.send_message(message.chat.id, stats, parse_mode="Markdown")

# --- חלק האתר ---
@app.route('/')
def home():
    user_id = request.args.get('user_id')
    balance = users_db.get(str(user_id), {}).get("balance", 0) if user_id else 0
    return f"<body style='background:#000;color:#d4af37;text-align:center;font-family:sans-serif;padding-top:50px;'>" \
           f"<h1>EMPIRE STAKES</h1><h2>Your Balance: ₪{balance}</h2></body>"

def run_bot():
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=10000)
