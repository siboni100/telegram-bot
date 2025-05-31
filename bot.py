import telebot
from telebot import types
from flask import Flask, request
import os

TOKEN = '7809342094:AAGpLE7T5E-Spvd7Gzv7cpSDKTpf_HDpHAo'
ADMIN_CHAT_ID = 7759457391  # שים את ה-ID שלך פה
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

user_data = {}

# מחירים
prices = {
    'greenhouse_5': 150, 'greenhouse_10': 250, 'greenhouse_20': 400,
    'vape_1': 300, 'vape_2': 550,
    'medica_1': 400, 'medica_2': 700, 'medica_3': 1000,
    'boutique_5': 200, 'boutique_10': 350, 'boutique_20': 650,
    'moroccan_1':1200, 'moroccan_2': 2000,
}

# סוגי שקיות
bags = {
    'סטיבה': ['תל אביב', 'גין גאי', 'אלסקה', 'אולטרא סאוור', 'טי סי', 'סינרג׳י', 'מרמלדה', 'תכלת', 'מיאמי סקי', 'גי דיזל', 'אורגינל גי סי'],
    'אינדיקה': ['קוטון קנדי', 'פרפל גלו', 'מירקל אילן קוקיז', 'בלו מון', 'קריטיקל טיקס', 'תלתן סגול', 'בראוניז', 'הולנדי', 'הינדו', 'רפאל', 'גורילה גלו'],
    'היברידי': ['הי מאיה', 'סטרוננה', 'בלו אמרלד', 'בנגו', 'אטומטיק', 'וודינג סי קי']
}

# התחלה
@bot.message_handler(commands=['start'])
def start(message):
    user_data[message.chat.id] = {}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('חשיש', 'וייפים')
    markup.add('בוטיק', 'חממה', 'שקיות רפואי')
    bot.send_message(message.chat.id, "ברוך הבא למיידי פארם, בחר קטגוריה:", reply_markup=markup)

# הודעות כלליות
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    cid = message.chat.id
    text = message.text

    if text == 'חשיש':
        video = open('images/moroccan.MP4', 'rb')
        bot.send_video(cid, video)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("1 = 1200₪", callback_data='moroccan_1'))
        markup.add(types.InlineKeyboardButton("2 = 2000₪", callback_data='moroccan_2'))
        bot.send_message(cid, "בחר כמות:", reply_markup=markup)
    elif text == 'וייפים':
        video = open('images/and_beautiful.MP4', 'rb')
        bot.send_video(cid, video)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("1 = 300₪", callback_data='vape_1'))
        markup.add(types.InlineKeyboardButton("2 = 550₪", callback_data='vape_2'))
        bot.send_message(cid, "בחר כמות:", reply_markup=markup)
    elif text == 'חממה':
        photo = open('images/greenhouse.jpg', 'rb')
        bot.send_photo(cid, photo)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("5 גרם - 150₪", callback_data='greenhouse_5'))
        markup.add(types.InlineKeyboardButton("10 גרם - 250₪", callback_data='greenhouse_10'))
        markup.add(types.InlineKeyboardButton("20 גרם - 400₪", callback_data='greenhouse_20'))
        bot.send_message(cid, "בחר כמות:", reply_markup=markup)
    elif text == 'בוטיק':
        photo = open('images/boutique.jpg', 'rb')
        bot.send_photo(cid, photo)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("5 = 200₪", callback_data='boutique_1'))
        markup.add(types.InlineKeyboardButton("10 = 350₪", callback_data='boutique_2'))
        markup.add(types.InlineKeyboardButton("20 = 650₪", callback_data='boutique_3'))
        bot.send_message(cid, "בחר כמות:", reply_markup=markup)
    elif text == 'שקיות רפואי':
        photo = open('images/medica.jpg', 'rb')
        bot.send_photo(cid, photo)
        markup = types.InlineKeyboardMarkup()
        for category in bags:
            markup.add(types.InlineKeyboardButton(category, callback_data=f'bag_type_{category}'))
        bot.send_message(cid, "בחר סוג:", reply_markup=markup)

# לחיצה על כפתורים
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    cid = call.message.chat.id
    data = call.data

    if data.startswith('bag_type_'):
        category = data.replace('bag_type_', '')
        markup = types.InlineKeyboardMarkup()
        for item in bags[category]:
            markup.add(types.InlineKeyboardButton(item, callback_data=f'bag_{item}'))
        bot.send_message(cid, f"בחר שקית ({category}):", reply_markup=markup)
    elif data.startswith('bag_'):
        bag = data.replace('bag_', '')
        user_data[cid]['item'] = bag
        ask_delivery(call.message)
    else:
        user_data[cid]['item'] = data
        ask_delivery(call.message)

def send_summary(cid):
    data = user_data.get(cid, {})

    product = data.get('product', 'לא ידוע')
    type_ = data.get('type', 'לא נבחר')
    quantity = data.get('quantity', 1)
    price = data.get('price', 'לא נבחר')
    method = data.get('method', 'לא נבחר')
    address = data.get('address', '---') if method == 'משלוח' else '---'
    contact = data.get('contact', '---')
    username = f"@{bot.get_chat(cid).username}" if bot.get_chat(cid).username else f"ID: {cid}"

    if method == 'משלוח':
        summary = (
            f"🧾 *סיכום הזמנה:*\n"
            f"👤 לקוח: {username}\n"
            f"📞 פרטים: {contact}\n"
            f"📍 כתובת: {address}\n"
            f"📦 מוצר: {product}\n"
            f"🧪 סוג: {type_}\n"
            f"🔢 כמות: {quantity}\n"
            f"💸 מחיר: {price}₪\n"
            f"🚚 שיטה: {method}"
        )
    else:  # איסוף
        summary = (
            f"🧾 *סיכום הזמנה:*\n"
            f"👤 לקוח: {username}\n"
            f"📞 פרטים: {contact}\n"
            f"📦 מוצר: {product}\n"
            f"🧪 סוג: {type_}\n"
            f"🔢 כמות: {quantity}\n"
            f"💸 מחיר: {price}₪\n"
            f"🚚 שיטה: {method}"
        )

    # שלח למשתמש
    bot.send_message(cid, summary, parse_mode="Markdown")

    # שלח למנהל
    bot.send_message(ADMIN_CHAT_ID, f"📥 הזמנה חדשה:\n{summary}", parse_mode="Markdown")

# Webhook
@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "ok", 200

@app.route("/", methods=['GET'])
def index():
    return "Bot is running", 200

if __name__ == '__main__' :
    bot.remove_webhook()
    bot.set_webhook(url=f"https://telegram-bot-zzi5.onrender.com/7809342094:AAGpLE7T5E-Spvd7Gzv7cpSDKTpf_HDpHAo")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)