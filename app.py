import telebot
from telebot import types
import threading
import json
import os
from flask import Flask, request

# ================= הגדרות אישיות =================
TOKEN = '8385525865:AAEgxmw8Sufo35fzEpVT50VFtP4wvhAN3pc'
ADMIN_ID = 6504579711  # ה-ID שלך לקבלת התראות
GROUP_URL = "https://t.me/+W1FOgCfwvKczNDg0" # קישור לקבוצה
URL_SITE = "https://empire-casino.onrender.com" # קישור לאתר
# ===============================================

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
DB_FILE = "casino_db.json"

# טעינה ושמירה של מסד נתונים
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f: return json.load(f)
    return {}

def save_db(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f, indent=4)

users_db = load_db()

# יצירת מקלדת ראשית עם 5 אפשרויות
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🔗 כניסה לקבוצה")
    btn2 = types.KeyboardButton("💰 הפקדה / משיכה")
    btn3 = types.KeyboardButton("🎰 כניסה למשחקים")
    btn4 = types.KeyboardButton("💵 היתרה שלי")
    btn5 = types.KeyboardButton("👤 פרטי שחקן")
    markup.add(btn3) # משחקים הכי גדול
    markup.add(btn1, btn2)
    markup.add(btn4, btn5)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    if uid not in users_db:
        # יצירת פרופיל שחקן חדש עם כל הנתונים שביקשת
        users_db[uid] = {
            "balance": 0,
            "total_deposited": 0,
            "total_withdrawn": 0,
            "total_lost": 0,
            "favorite_game": "עדיין לא שיחק"
        }
        save_db(users_db)
    
    bot.send_message(message.chat.id, "🏆 **ברוך הבא ל-EMPIRE STAKES!**\nבחר אפשרות מהתפריט למטה:", 
                     parse_mode="Markdown", reply_markup=main_menu())

@bot.message_handler(func=lambda m: True)
def handle_menu(message):
    uid = str(message.from_user.id)
    name = message.from_user.first_name
    text = message.text

    if text == "🔗 כניסה לקבוצה":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("לחץ כאן להצטרפות 📢", url=GROUP_URL))
        bot.send_message(message.chat.id, "הצטרף לקהילה שלנו כדי להישאר מעודכן:", reply_markup=markup)

    elif text == "💰 הפקדה / משיכה":
        # שולח למשתמש הוראות
        bot.send_message(message.chat.id, "בקשתך הועברה למנהל. הוא ייצור איתך קשר בהקדם!")
        # שולח לך (המנהל) התראה!
        bot.send_message(ADMIN_ID, f"🔔 **בקשה חדשה!**\nהמשתמש {name} (ID: `{uid}`) רוצה לבצע הפקדה/משיכה.\nלחץ כדי לדבר איתו: [קישור למשתמש](tg://user?id={uid})", parse_mode="Markdown")

    elif text == "🎰 כניסה למשחקים":
        markup = types.InlineKeyboardMarkup()
        game_url = f"{URL_SITE}/?user_id={uid}"
        markup.add(types.InlineKeyboardButton("פתח קזינו 🌐", url=game_url))
        bot.send_message(message.chat.id, "המזל מחכה לך בפנים! לחץ על הכפתור:", reply_markup=markup)

    elif text == "💵 היתרה שלי":
        balance = users_db.get(uid, {}).get("balance", 0)
        bot.send_message(message.chat.id, f"💰 היתרה הנוכחית שלך היא: **₪{balance}**", parse_mode="Markdown")

    elif text == "👤 פרטי שחקן":
        user = users_db.get(uid, {})
        stats = (
            f"👤 **כרטיס שחקן: {name}**\n\n"
            f"💵 יתרה: **₪{user.get('balance', 0)}**\n"
            f"📥 סך הפקדות: ₪{user.get('total_deposited', 0)}\n"
            f"📤 סך משיכות: ₪{user.get('total_withdrawn', 0)}\n"
            f"📉 סך הפסדים: ₪{user.get('total_lost', 0)}\n"
            f"🎮 משחק מועדף: {user.get('favorite_game', 'אין')}"
        )
        bot.send_message(message.chat.id, stats, parse_mode="Markdown")

# פקודת ניהול להטענת כסף (רק אתה יכול)
@bot.message_handler(commands=['set'])
def set_balance(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        _, target_id, amount = message.text.split()
        amount = int(amount)
        if target_id in users_db:
            users_db[target_id]["balance"] = amount
            # אם זו הפקדה, נוסיף לסטטיסטיקה של "סך הפקדות"
            users_db[target_id]["total_deposited"] += amount 
            save_db(users_db)
            bot.reply_to(message, f"✅ היתרה של {target_id} עודכנה ל-₪{amount}")
            bot.send_message(target_id, f"💰 חשבונך הוטען ב-₪{amount}! בהצלחה.")
    except:
        bot.reply_to(message, "שימוש: `/set ID amount`", parse_mode="Markdown")

# --- אתר אינטרנט בסיסי ---
@app.route('/')
def home():
    user_id = request.args.get('user_id')
    balance = users_db.get(str(user_id), {}).get("balance", 0) if user_id else 0
    return f"<body style='background:#000;color:#d4af37;text-align:center;'><h1>EMPIRE STAKES</h1><h2>Your Balance: ₪{balance}</h2></body>"

def run_bot():
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=10000)
