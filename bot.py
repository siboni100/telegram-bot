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
    'boutique_1': 1200, 'boutique_2': 2000
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
        markup.add(types.InlineKeyboardButton("1 = 1200₪", callback_data='boutique_1'))
        markup.add(types.InlineKeyboardButton("2 = 2000₪", callback_data='boutique_2'))
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

def ask_delivery(msg):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("משלוח", "איסוף")
    bot.send_message(msg.chat.id, "איך תרצה לקבל את ההזמנה?", reply_markup=markup)
@bot.message_handler(func=lambda m: m.text in ['משלוח', 'איסוף'])
def handle_delivery(message):
    cid = message.chat.id
    method = message.text
    user_data[cid]['method'] = method
    if method == 'משלוח':
        bot.send_message(cid, "אנא שלח כתובת מלאה:")
        bot.register_next_step_handler(message, get_address)
    else:
        bot.send_message(cid, "אנא שלח שם מלא ומספר טלפון:")
        bot.register_next_step_handler(message, get_contact)

def get_address(message):
    cid = message.chat.id
    user_data[cid]['address'] = message.text
    send_summary(cid)

def get_contact(message):
    cid = message.chat.id
    user_data[cid]['contact'] = message.text
    send_summary(cid)

def send_summary(cid):
    data = user_data[cid]
    item = data.get('item', 'לא נבחר')
    method = data.get('method')
    details = data.get('address') if method == 'משלוח' else data.get('contact')
    price = prices.get(item, 'לא ידוע')

    summary = f"🛒 הזמנה חדשה\n\nמוצר: {item}\nמחיר: {price}₪\nשיטה: {method}\nפרטים: {details}"
    bot.send_message(cid, "תודה על ההזמנה ❤️")
    bot.send_message(ADMIN_CHAT_ID, summary)

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
    bot.set_webhook(url=f"https://telegram-bot-zzi5.onrender.com/7809342094:AAGpLE7T5E-Spvd7Gzv7cpSDKTpf_HDpHAo)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)