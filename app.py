import telebot
from telebot import types
import threading
from flask import Flask

# --- הגדרות אישיות (תעדכן כאן!) ---
TOKEN = '8385525865:AAEgxmw8Sufo35fzEpVT50VFtP4wvhAN3pc' # שים את הטוקן שלך
ADMIN_ID = 6504579711 # שים את ה-ID שלך (מספר בלבד)
URL_SITE = "https://empire-casino.onrender.com" # הקישור שלך מ-Render

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# מסד נתונים זמני (יתאפס בריסטארט של השרת)
users_db = {}

# --- פונקציות הבוט ---

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🎰 כניסה למשחקים"))
    markup.add(types.KeyboardButton("👤 ניהול חשבון"), types.KeyboardButton("💰 הפקדה / משיכה"))
    markup.add(types.KeyboardButton("💎 שירות לקוחות VIP"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    if uid not in users_db:
        users_db[uid] = 0
    bot.send_message(message.chat.id, "🏆 ברוך הבא ל-EMPIRE STAKES! 🏆\nחווית הקזינו היוקרתית ביותר בטלגרם.", reply_markup=main_menu())

@bot.message_handler(commands=['set'])
def set_balance(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        parts = message.text.split()
        target_id = parts[1]
        amount = int(parts[2])
        users_db[target_id] = amount
        bot.reply_to(message, f"✅ היתרה של {target_id} עודכנה ל-₪{amount}")
    except:
        bot.reply_to(message, "שימוש: /set ID סכום")

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    uid = str(message.from_user.id)
    text = message.text

    if "כניסה למשחקים" in text:
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("לחץ כאן לכניסה לאתר 🌐", url=URL_SITE)
        markup.add(btn)
        bot.send_message(message.chat.id, "בהצלחה! לחץ למטה כדי להתחיל לשחק:", reply_markup=markup)

    elif "ניהול חשבון" in text:
        balance = users_db.get(uid, 0)
        bot.send_message(message.chat.id, f"📋 פרטי חשבון:\n🆔 מזהה: {uid}\n💵 יתרה: ₪{balance}")

    elif "שירות לקוחות" in text or "VIP" in text:
        bot.send_message(message.chat.id, "👑 מוקד VIP זמין עבורך!\nלכל שאלה, פנה למנהל.")

    elif "הפקדה" in text:
        bot.send_message(message.chat.id, "💰 להפקדה או משיכה, פנה למנהל עם ה-ID שלך.")

# --- חלק האתר (HTML + CSS) ---

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Empire Stakes</title>
        <style>
            body { background: #000; color: #d4af37; font-family: Arial; text-align: center; margin: 0; }
            .header { padding: 40px; border-bottom: 2px solid #d4af37; background: #111; }
            h1 { margin: 0; font-size: 2.5em; letter-spacing: 2px; }
            .balance { background: #1a1a1a; padding: 20px; margin: 20px auto; width: 80%; border-radius: 10px; border: 1px solid #d4af37; font-size: 1.5em; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; padding: 20px; }
            .card { background: #111; border: 1px solid #333; padding: 25px; border-radius: 12px; }
            .play-btn { background: #d4af37; color: #000; border: none; padding: 10px; width: 100%; border-radius: 5px; font-weight: bold; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="header"><h1>EMPIRE STAKES</h1></div>
        <div class="balance">💰 יתרה: ₪0</div>
        <div class="grid">
            <div class="card"><h3>רולטה</h3><button class="play-btn">שחק</button></div>
            <div class="card"><h3>סלוטים</h3><button class="play-btn">שחק</button></div>
            <div class="card"><h3>בלאק ג'ק</h3><button class="play-btn">שחק</button></div>
            <div class="card"><h3>פוקר</h3><button class="play-btn">שחק</button></div>
        </div>
    </body>
    </html>
    """

# --- הרצה משולבת ---

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    # הפעלת הבוט בטרד נפרד
    threading.Thread(target=run_bot).start()
    # הפעלת האתר על פורט 10000 של Render
    app.run(host='0.0.0.0', port=10000)
