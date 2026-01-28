from flask import Flask, render_template, request
import telebot
from threading import Thread

app = Flask(__name__)

# שים פה את הטוקן שלך
TOKEN = "Y8385525865:AAEgxmw8Sufo35fzEpVT50VFtP4wvhAN3pc"
bot = telebot.TeleBot(TOKEN)

# מסד נתונים ריק - כולם מתחילים מ-0
users_db = {}

@app.route('/')
def home():
    user_id = request.args.get('id')
    # אם המשתמש לא קיים, הוא יראה 0 שקלים
    user = users_db.get(user_id, {"name": "שחקן", "balance": "0"})
    return render_template('index.html', user=user)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    
    # רישום המשתמש במערכת עם יתרה 0
    if user_id not in users_db:
        users_db[user_id] = {"name": user_name, "balance": "0"}

    markup = telebot.types.InlineKeyboardMarkup()
    # הכפתור שמוביל לאתר שלך
    btn = telebot.types.InlineKeyboardButton(
        text="🏰 כניסה ל-EMPIRE STAKES", 
        url=f"http://127.0.0.1:5000/?id={user_id}"
    )
    markup.add(btn)
    
    bot.reply_to(message, f"שלום {user_name}, ברוך הבא ל-Empire Stakes.\nהיתרה שלך מעודכנת באתר.", reply_markup=markup)

def run_flask():
    app.run(port=5000, debug=False, use_reloader=False)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    print("--- המערכת רצה! כנס לטלגרם ותלחץ /start ---")
    bot.polling(none_stop=True)
    
    if __name__ == "__main__":
    # בשרת אנחנו לא צריכים Threads, השרת מריץ את Flask לבד
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))