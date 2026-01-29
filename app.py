import telebot
from telebot import types
import threading
from flask import Flask, request
from pymongo import MongoClient
import time
import os

# ================= פרטי המערכת =================
TOKEN = '8385525865:AAFqLhwgBgs5CRKHhNUPlRcWilTFidWzWec'
ADMIN_ID = 6504579711
URL_SITE = "https://empire-stakes.onrender.com"
MONGO_URI = "mongodb+srv://shilomlca294_db_user:VIj9XsxyHfKBbajY@empirestakes.xzrducv.mongodb.net/?appName=EmpireStakes&tlsAllowInvalidCertificates=true"

cluster = MongoClient(MONGO_URI)
db = cluster["casino_database"]
users_col = db["users"]
# ==============================================

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# פונקציית עזר לשליפת נתונים
def get_user_data(uid):
    uid = str(uid)
    user = users_col.find_one({"_id": uid})
    if not user:
        user = {"_id": uid, "balance": 0, "total_deposited": 0}
        users_col.insert_one(user)
    return user

# --- ניהול פקודות בוט ---
@bot.message_handler(commands=['start'])
def start(message):
    get_user_data(message.from_user.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🎰 כניסה למשחקים"))
    bot.send_message(message.chat.id, "🏆 **EMPIRE STAKES**\nהקזינו שלך מוכן!", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🎰 כניסה למשחקים")
def play_button(message):
    uid = str(message.from_user.id)
    markup = types.InlineKeyboardMarkup()
    # הקישור המדויק כולל ה-ID
    markup.add(types.InlineKeyboardButton("לחץ כאן לכניסה 🌐", url=f"{URL_SITE}/?user_id={uid}"))
    bot.send_message(message.chat.id, "המזל מחכה לך בפנים:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and "טען" in m.text)
def admin_load(message):
    try:
        _, uid, amt = message.text.split()
        user = get_user_data(uid)
        new_bal = user['balance'] + int(amt)
        users_col.update_one({"_id": uid}, {"$set": {"balance": new_bal}})
        bot.reply_to(message, f"✅ נטענו ₪{amt}")
    except: bot.reply_to(message, "טעות בפורמט")

# --- דף הבית (האתר) ---
@app.route('/')
def home():
    user_id = request.args.get('user_id')
    # אם אין ID, נציג דף כללי כדי למנוע Not Found
    if not user_id:
        return "<body style='background:#000;color:#d4af37;text-align:center;padding-top:100px;'><h1>EMPIRE STAKES</h1><p>אנא היכנס דרך הבוט בטלגרם</p></body>"
    
    user = users_col.find_one({"_id": str(user_id)})
    balance = user["balance"] if user else 0
    
    return f"""
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Empire Stakes</title>
        <style>
            body {{ background: #0a0a0a; color: white; font-family: sans-serif; text-align: center; margin: 0; }}
            .gold {{ color: #d4af37; font-size: 2.5em; margin-top: 50px; }}
            .balance {{ font-size: 1.5em; border: 2px solid #d4af37; display: inline-block; padding: 10px 20px; border-radius: 20px; margin: 20px; }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; padding: 20px; }}
            .card {{ background: #1a1a1a; padding: 30px; border-radius: 15px; border: 1px solid #333; }}
        </style>
    </head>
    <body>
        <h1 class="gold">EMPIRE STAKES</h1>
        <div class="balance">יתרה: ₪{balance}</div>
        <div class="grid">
            <div class="card">🎰<br>סלוטים</div>
            <div class="card">🎡<br>רולטה</div>
        </div>
    </body>
    </html>
    """

# --- הרצה ---
def run_bot():
    while True:
        try:
            bot.remove_webhook()
            bot.infinity_polling(timeout=60)
        except: time.sleep(5)

if __name__ == "__main__":
    # הרצת הבוט ב-Thread נפרד
    threading.Thread(target=run_bot, daemon=True).start()
    # הרצת האתר על הפורט של Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
