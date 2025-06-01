import telebot
from telebot import types
import os
from flask import Flask, request

TOKEN = '7809342094:AAGpLE7T5E-Spvd7Gzv7cpSDKTpf_HDpHAo'
ADMIN_CHAT_ID = 7759457391
GROUP_CHAT_ID = 1002639815887

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# טעמים של וייפים
vape_flavors = [
    "Frozen grapes", "Apple jam", "Papaya",
    "Blu velvet", "Blu frootz", "LA Zkittlez"
]

# נתיב לתמונה
START_IMAGE_PATH = "images/start.jpg"  # תמונה לפתיחה

# פקודת start
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("וייפים", "שקיות")
    if os.path.exists(START_IMAGE_PATH):
        with open(START_IMAGE_PATH, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption="ברוך הבא ל-Miday Pharma 🌿", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "ברוך הבא ל-Miday Pharma 🌿", reply_markup=markup)

# בחירה בין וייפים לשקיות
@bot.message_handler(func=lambda message: message.text == "וייפים")
def handle_vapes(message):
    markup = types.InlineKeyboardMarkup()
    for flavor in vape_flavors:
        markup.add(types.InlineKeyboardButton(text=flavor, callback_data=f"vape_{flavor}"))
    bot.send_message(message.chat.id, "בחר טעם:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "שקיות")
def handle_bags(message):
    bot.send_message(message.chat.id, ✳️ זמנית רק וייפים זמינים.")

# בחירת טעם → בחירת כמות
@bot.callback_query_handler(func=lambda call: call.data.startswith("vape_"))
def choose_vape_quantity(call):
    flavor = call.data.replace("vape_", "")
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("1 יחידה – 300 ₪", callback_data=f"buy_{flavor}_1"))
    markup.add(types.InlineKeyboardButton("2 יחידות – 550 ₪", callback_data=f"buy_{flavor}_2"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=f"טעם נבחר: {flavor}\nבחר כמות:", reply_markup=markup)

# שליחת הזמנה למנהל
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def confirm_order(call):
    parts = call.data.split("_")
    flavor = parts[1]
    quantity = parts[2]
    price = "300 ₪" if quantity == "1" else "550 ₪"

    # הודעה למנהל (בקבוצה)
    order_text = f"התקבלה הזמנה חדשה:\n🌀 מוצר: וייפ\n🌸 טעם: {flavor}\n🔢 כמות: {quantity}\n💰 מחיר: {price}\n👤 משתמש: @{call.from_user.username or 'ללא'}"
    bot.send_message(GROUP_CHAT_ID, order_text)

    # הודעת תודה למשתמש
    bot.send_message(call.message.chat.id, "✅ תודה שבחרת Miday Pharma!")

# פקודה לשליחת פוסט לקבוצה
@bot.message_handler(commands=['post'])
def send_post(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("שקיות חדשות", callback_data="post_bags"))
    markup.add(types.InlineKeyboardButton("וייפים בטעמים", callback_data="post_vapes"))
    markup.add(types.InlineKeyboardButton("פרחים בוטיקיים", callback_data="post_flowers"))
    markup.add(types.InlineKeyboardButton("סבב משלוחים", callback_data="post_delivery"))
    bot.send_message(message.chat.id, "בחר פוסט לשליחה לקבוצה:", reply_markup=markup)

# שליחת הפוסט שנבחר לקבוצה בלבד
@bot.callback_query_handler(func=lambda call: call.data.startswith("post_"))
def send_group_post(call):
    posts = {
        "post_bags": ("🛍️ הגיעו שקיות חדשות במגוון זנים!"),
        "post_vapes": ("💨 וייפים בטעמים מטריפים במלאי!"),
        "post_flowers": ("🌺 פרחים בוטיקיים טריים עכשיו זמינים"),
        "post_delivery": ("🚚 סבב משלוחים יוצא לדרך – הזמינו עכשיו!")
    }
    text = posts.get(call.data)
    if text:
        bot.send_message(GROUP_CHAT_ID, text)
        bot.answer_callback_query(call.id, "הפוסט נשלח לקבוצה!")

# Webhook ל-Render או Flask
@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return 'ok', 200

@app.route('/')
def index():
    return "Miday Pharma Bot"

if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 5000))
    bot.remove_webhook()
    bot.set_webhook(url=f"https://telegram-bot-zzi5.onrender.com/7809342094:AAGpLE7T5E-Spvd7Gzv7cpSDKTpf_HDpHAo")
    app.run(host="0.0.0.0", port=port)
