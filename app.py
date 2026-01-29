import telebot
from telebot import types
import threading
from flask import Flask, request
from pymongo import MongoClient
import time

# ================= פרטי המערכת שלך =================
TOKEN = '8385525865:AAFqLhwgBgs5CRKHhNUPlRcWilTFidWzWec'
ADMIN_ID = 6504579711
GROUP_URL = "https://t.me/+W1FOgCfwvKczNDg0"
URL_SITE = "https://empire-stakes.onrender.com"
MONGO_URI = "mongodb+srv://shilomlca294_db_user:VIj9XsxyHfKBbajY@empirestakes.xzrducv.mongodb.net/?appName=EmpireStakes"

# חיבור ל-MongoDB (הכספת)
cluster = MongoClient(MONGO_URI)
db = cluster["casino_database"]
users_col = db["users"]
# ===============================================

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- פונקציות עבודה מול הכספת (MongoDB) ---
def get_user_data(uid):
    uid = str(uid)
    user = users_col.find_one({"_id": uid})
    if not user:
        user = {
            "_id": uid, 
            "balance": 0, 
            "total_deposited": 0, 
            "total_withdrawn": 0, 
            "total_lost": 0, 
            "favorite_game": "אין"
        }
        users_col.insert_one(user)
    return user

def update_user_data(uid, update_fields):
    users_col.update_one({"_id": str(uid)}, {"$set": update_fields})

# --- פקודות ניהול (טען, הסר, מינוס) ---
@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and any(word in m.text for word in ["טען", "הסר", "מינוס"]))
def admin_commands(message):
    try:
        parts = message.text.split()
        command, target_id, amount = parts[0], parts[1], int(parts[2])
        user = get_user_data(target_id)

        if command == "טען":
            new_balance = user["balance"] + amount
            new_deposited = user["total_deposited"] + amount
            update_user_data(target_id, {"balance": new_balance, "total_deposited": new_deposited})
            bot.send_message(target_id, f"💰 **חשבונך הוטען!**\nנוספו: ₪{amount}\nיתרה חדשה: ₪{new_balance}", parse_mode="Markdown")
            res_msg = f"✅ טענתי ₪{amount} ל-{target_id}"

        elif command == "הסר":
            new_balance = user["balance"] - amount
            new_withdrawn = user["total_withdrawn"] + amount
            update_user_data(target_id, {"balance": new_balance, "total_withdrawn": new_withdrawn})
            bot.send_message(target_id, f"💸 **משיכה בוצעה!**\nהוסרו: ₪{amount}\nיתרה חדשה: ₪{new_balance}", parse_mode="Markdown")
            res_msg = f"✅ הסרתי ₪{amount} מ-{target_id}"

        elif command == "מינוס":
            update_user_data(target_id, {"balance": -amount})
            bot.send_message(target_id, f"⛔ **חשבונך במינוס!**\nיתרה: ₪{amount}-", parse_mode="Markdown")
            res_msg = f"⚠️ {target_id} הוכנס למינוס ₪{amount}-"

        bot.reply_to(message, res_msg)
    except:
        bot.reply_to(message, "⚠️ פורמט לא תקין! דוגמה: `טען 12345 500`", parse_mode="Markdown")

# --- תפריטים ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🎰 כניסה למשחקים"))
    markup.add(types.KeyboardButton("🔗 כניסה לקבוצה"), types.KeyboardButton("💰 הפקדה / משיכה"))
    markup.add(types.KeyboardButton("💵 היתרה שלי"), types.KeyboardButton("👤 פרטי שחקן"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    get_user_data(message.from_user.id)
    bot.send_message(message.chat.id, "🏆 **ברוך הבא ל-EMPIRE STAKES!**\nהיתרה שלך שמורה ומאובטחת.", 
                     parse_mode="Markdown", reply_markup=main_menu())

@bot.message_handler(func=lambda m: True)
def handle_menu(message):
    uid = str(message.from_user.id)
    text = message.text
    user = get_user_data(uid)

    if text == "🎰 כניסה למשחקים":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("פתח קזינו 🌐", url=f"{URL_SITE}/?user_id={uid}"))
        bot.send_message(message.chat.id, "🎰 המזל איתך! לחץ על הכפתור:", reply_markup=markup)
    elif text == "🔗 כניסה לקבוצה":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("להצטרפות 📢", url=GROUP_URL))
        bot.send_message(message.chat.id, "לחץ למטה לכניסה:", reply_markup=markup)
    elif text == "💰 הפקדה / משיכה":
        bot.send_message(message.chat.id, "📩 בקשתך נשלחה למנהל.")
        bot.send_message(ADMIN_ID, f"🔔 **בקשת הפקדה/משיכה!**\nID: `{uid}`", parse_mode="Markdown")
    elif text == "💵 היתרה שלי":
        bot.send_message(message.chat.id, f"💰 היתרה שלך: **₪{user['balance']}**", parse_mode="Markdown")
    elif text == "👤 פרטי שחקן":
        stats = (f"👤 **כרטיס שחקן VIP**\n\n"
                 f"💵 יתרה: **₪{user['balance']}**\n"
                 f"📥 סך הפקדות: ₪{user['total_deposited']}\n"
                 f"📤 סך משיכות: ₪{user['total_withdrawn']}")
        bot.send_message(message.chat.id, stats, parse_mode="Markdown")

# --- חלק האתר ---
@app.route('/')
def home():
    user_id = request.args.get('user_id')
    user = users_col.find_one({"_id": str(user_id)}) if user_id else None
    balance = user["balance"] if user else 0
    return f"<body style='background:#000;color:#d4af37;text-align:center;font-family:sans-serif;padding-top:50px;'>" \
           f"<h1>EMPIRE STAKES</h1><h2>Your Balance: ₪{balance}</h2></body>"

def run_bot():
    while True:
        try:
            bot.infinity_polling(timeout=60, skip_pending=True)
        except Exception as e:
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=10000)
