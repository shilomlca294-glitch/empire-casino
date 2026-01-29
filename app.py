import telebot
from telebot import types
import threading
from flask import Flask, request
from pymongo import MongoClient
import time

# ================= פרטי המערכת המעודכנים =================
TOKEN = '8385525865:AAFqLhwgBgs5CRKHhNUPlRcWilTFidWzWec'
ADMIN_ID = 6504579711
GROUP_URL = "https://t.me/+W1FOgCfwvKczNDg0"
URL_SITE = "https://empire-stakes.onrender.com"
# חיבור ל-MongoDB כולל תיקון SSL
MONGO_URI = "mongodb+srv://shilomlca294_db_user:VIj9XsxyHfKBbajY@empirestakes.xzrducv.mongodb.net/?appName=EmpireStakes&tlsAllowInvalidCertificates=true"

cluster = MongoClient(MONGO_URI)
db = cluster["casino_database"]
users_col = db["users"]
# =======================================================

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- פונקציות מסד נתונים (MongoDB) ---
def get_user_data(uid):
    uid = str(uid)
    user = users_col.find_one({"_id": uid})
    if not user:
        user = {
            "_id": uid, 
            "balance": 0, 
            "total_deposited": 0, 
            "total_withdrawn": 0
        }
        users_col.insert_one(user)
    return user

def update_user_data(uid, update_fields):
    users_col.update_one({"_id": str(uid)}, {"$set": update_fields})

# --- פקודות ניהול ---
@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and any(word in m.text for word in ["טען", "הסר", "מינוס"]))
def admin_commands(message):
    try:
        parts = message.text.split()
        command, target_id, amount = parts[0], parts[1], int(parts[2])
        user = get_user_data(target_id)

        if command == "טען":
            new_balance = user["balance"] + amount
            update_user_data(target_id, {"balance": new_balance, "total_deposited": user["total_deposited"] + amount})
            bot.send_message(target_id, f"💰 **חשבונך הוטען!**\nנוספו: ₪{amount}\nיתרה חדשה: ₪{new_balance}", parse_mode="Markdown")
            res_msg = f"✅ טענתי ₪{amount} ל-{target_id}"
        elif command == "הסר":
            new_balance = user["balance"] - amount
            update_user_data(target_id, {"balance": new_balance})
            res_msg = f"✅ הסרתי ₪{amount} מ-{target_id}"
        elif command == "מינוס":
            update_user_data(target_id, {"balance": -amount})
            res_msg = f"⚠️ {target_id} הוכנס למינוס ₪{amount}-"

        bot.reply_to(message, res_msg)
    except:
        bot.reply_to(message, "❌ שגיאה בפורמט. דוגמה: `טען 12345 500`")

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
    bot.send_message(message.chat.id, "🏆 **ברוך הבא ל-EMPIRE STAKES!**", 
                     parse_mode="Markdown", reply_markup=main_menu())

@bot.message_handler(func=lambda m: True)
def handle_menu(message):
    uid = str(message.from_user.id)
    user = get_user_data(uid)

    if message.text == "🎰 כניסה למשחקים":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("פתח קזינו 🌐", url=f"{URL_SITE}/?user_id={uid}"))
        bot.send_message(message.chat.id, "🎰 המזל איתך! לחץ על הכפתור:", reply_markup=markup)
    elif message.text == "💵 היתרה שלי":
        bot.send_message(message.chat.id, f"💰 היתרה שלך: **₪{user['balance']}**", parse_mode="Markdown")
    elif message.text == "💰 הפקדה / משיכה":
        bot.send_message(message.chat.id, "📩 בקשתך נשלחה למנהל.")
        bot.send_message(ADMIN_ID, f"🔔 **בקשה חדשה!**\nID: `{uid}`", parse_mode="Markdown")
    elif message.text == "👤 פרטי שחקן":
        stats = f"👤 **כרטיס שחקן VIP**\n\n💵 יתרה: **₪{user['balance']}**\n📥 סך הפקדות: ₪{user['total_deposited']}"
        bot.send_message(message.chat.id, stats, parse_mode="Markdown")

# --- חלק האתר המעוצב ---
@app.route('/')
def home():
    user_id = request.args.get('user_id')
    user = users_col.find_one({"_id": str(user_id)}) if user_id else None
    balance = user["balance"] if user else 0
    
    return f"""
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Empire Stakes | Lobby</title>
        <link href="https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;700&display=swap" rel="stylesheet">
        <style>
            body {{ background: #0a0a0a; color: white; font-family: 'Assistant', sans-serif; margin: 0; padding: 0; text-align: center; }}
            .header {{ background: linear-gradient(145deg, #1a1a1a, #000); padding: 30px; border-bottom: 2px solid #d4af37; box-shadow: 0 4px 15px rgba(212, 175, 55, 0.2); }}
            h1 {{ color: #d4af37; font-size: 2.5em; margin: 0; letter-spacing: 2px; text-transform: uppercase; }}
            .balance-box {{ background: rgba(212, 175, 55, 0.1); border: 1px solid #d4af37; display: inline-block; padding: 10px 30px; border-radius: 50px; margin-top: 15px; font-size: 1.2em; }}
            .balance-amount {{ color: #d4af37; font-weight: bold; }}
            .game-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 15px; padding: 20px; max-width: 800px; margin: 0 auto; }}
            .game-card {{ background: #1a1a1a; border-radius: 15px; padding: 20px; border: 1px solid #333; transition: 0.3s; }}
            .game-card:hover {{ border-color: #d4af37; transform: scale(1.05); }}
            .game-icon {{ font-size: 2.5em; margin-bottom: 10px; display: block; }}
            .footer {{ margin-top: 40px; color: #555; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>EMPIRE STAKES</h1>
            <div class="balance-box">💰 יתרה: <span class="balance-amount">₪{balance}</span></div>
        </div>
        <div class="game-grid">
            <div class="game-card"><span class="game-icon">🎰</span><b>Slots</b></div>
            <div class="game-card"><span class="game-icon">🎡</span><b>Roulette</b></div>
            <div class="game-card"><span class="game-icon">🚀</span><b>Aviator</b></div>
            <div class="game-card"><span class="game-icon">🃏</span><b>Poker</b></div>
        </div>
        <div class="footer">&copy; 2026 Empire Stakes Casino</div>
    </body>
    </html>
    """

def run_bot():
    while True:
        try:
            bot.remove_webhook()
            bot.infinity_polling(timeout=60, skip_pending=True)
        except:
            time.sleep(10)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=10000)
