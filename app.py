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
