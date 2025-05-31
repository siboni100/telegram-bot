import telebot
from telebot import types
from flask import Flask, request
import os

TOKEN = '7809342094:AAGpLE7T5E-Spvd7Gzv7cpSDKTpf_HDpHAo'
ADMIN_CHAT_ID = 7759457391
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

user_data = {}
steps = {}

# מחירים
prices = {
    'greenhouse_5': 150, 'greenhouse_10': 250, 'greenhouse_20': 400,
    'vape_1': 300, 'vape_2': 550,
    'medica_1': 400, 'medica_2': 700, 'medica_3': 1000,
    'boutique_5': 200, 'boutique_10': 350, 'boutique_20': 650,
    'moroccan_1': 1200, 'moroccan_2': 2000,
}

# סוגי שקיות
bags = {
    'סטיבה': ['תל אביב', 'גין גאי', 'אלסקה', 'אולטרא סאוור', 'טי סי', 'סינרג׳י', 'מרמלדה', 'תכלת', 'מיאמי סקי', 'גי דיזל', 'אורגינל גי סי'],
    'אינדיקה': ['קוטון קנדי', 'פרפל גלו', 'מירקל אילן קוקיז', 'בלו מון', 'קריטיקל טיקס', 'תלתן סגול', 'בראוניז', 'הולנדי', 'הינדו', 'רפאל', 'גורילה גלו'],
    'היברידי': ['הי מאיה', 'סטרוננה', 'בלו אמרלד', 'בנגו', 'אטומטיק', 'וודינג סי קי']
}

@bot.message_handler(commands=['start'])
def start(message):
    cid = message.chat.id
    user_data[cid] = {}
    markup = types.ReplyKeyboardRemove()
    bot.send_message(cid, "ברוך הבא למיידי פארם, בחר קטגוריה:", reply_markup=markup)
    main_menu(cid)

def main_menu(cid):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("חשיש", callback_data='menu_hashish'))
    markup.add(types.InlineKeyboardButton("וייפים", callback_data='menu_and_beautiful.MP4'))
    markup.add(types.InlineKeyboardButton("בוטיק", callback_data='menu_boutique'))
    markup.add(types.InlineKeyboardButton("חממה", callback_data='menu_greenhouse'))
    markup.add(types.InlineKeyboardButton("שקיות רפואי", callback_data='menu_medica'))
    bot.send_message(cid, "בחר קטגוריה:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    cid = call.message.chat.id
    data = call.data

    if data.startswith('menu_'):
        category = data.replace('menu_', '')
        if category == 'hashish':
            video = open('images/moroccan.MP4', 'rb')
            bot.send_video(cid, video)
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("1 = 1200₪", callback_data='moroccan_1'))
            markup.add(types.InlineKeyboardButton("2 = 2000₪", callback_data='moroccan_2'))
            bot.send_message(cid, "בחר כמות:", reply_markup=markup)

        elif category == 'and_beautiful.MP4':
            video = open('images/and_beautiful.MP4', 'rb')
            bot.send_video(cid, video)
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("1 = 300₪", callback_data='and_beautiful.MP4_1'))
            markup.add(types.InlineKeyboardButton("2 = 550₪", callback_data='and_beautiful.MP4_2'))
            bot.send_message(cid, "בחר כמות:", reply_markup=markup)

        elif category == 'greenhouse.jpg':
            photo = open('images/greenhouse.jpg', 'rb')
            bot.send_photo(cid, photo)
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("5 גרם - 150₪", callback_data='greenhouse_5'))
            markup.add(types.InlineKeyboardButton("10 גרם - 250₪", callback_data='greenhouse_10'))
            markup.add(types.InlineKeyboardButton("20 גרם - 400₪", callback_data='greenhouse_20'))
            bot.send_message(cid, "בחר כמות:", reply_markup=markup)

    elif category == 'boutique.jpg':
            photo = open('images/boutique.jpg', 'rb')
            bot.send_photo(cid, photo)
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("5 = 200₪", callback_data='boutique_5'))
            markup.add(types.InlineKeyboardButton("10 = 350₪", callback_data='boutique_10'))
            markup.add(types.InlineKeyboardButton("20 = 650₪", callback_data='boutique_20'))
            bot.send_message(cid, "בחר כמות:", reply_markup=markup)

    elif category == 'medica.jpg':
            photo = open('images/medica.jpg', 'rb')
            bot.send_photo(cid, photo)
            markup = types.InlineKeyboardMarkup()
            for cat in bags:
                markup.add(types.InlineKeyboardButton(cat, callback_data=f'bag_type_{cat}'))
            bot.send_message(cid, "בחר סוג:", reply_markup=markup)

    elif data.startswith('bag_type_'):
        category = data.replace('bag_type_', '')
        markup = types.InlineKeyboardMarkup()
    for item in bags[category]:
        markup.add(types.InlineKeyboardButton(item, callback_data=f'bag_{item}'))
        bot.send_message(cid, f"בחר שקית ({category}):", reply_markup=markup)

    elif data.startswith('bag_'):
        bag = data.replace('bag_', '')
        user_data[cid]['product'] = bag
        user_data[cid]['type'] = 'שקית רפואי'
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("1 = 400₪", callback_data='medica_1'))
        markup.add(types.InlineKeyboardButton("2 = 700₪", callback_data='medica_2'))
        markup.add(types.InlineKeyboardButton("3 = 1000₪", callback_data='medica_3'))
        bot.send_message(cid, "בחר כמות:", reply_markup=markup)

    elif data in prices :
        user_data[cid]['product'] = data
        user_data[cid]['price'] = prices[data]

        # אם מדובר במוצר שמכיל כבר כמות, נחלץ אותה מהשם (למשל greenhouse_5)
    if any(data.startswith(prefix) for prefix in ['greenhouse_', 'vape_', 'medica_', 'boutique_', 'moroccan_']):
            quantity = int(data.split('_')[-1])
            user_data[cid]['quantity'] = quantity
            ask_delivery(cid)
    else:
            ask_quantity(cid)

    elif data.startswith('quantity_'):
            quantity = int(data.replace('quantity_', ''))
            user_data[cid]['quantity'] = quantity
            ask_delivery(cid)

    elif data in ['delivery', 'pickup']:
            user_data[cid]['method'] = 'משלוח' if data == 'delivery' else 'איסוף'
            if data == 'delivery':
                bot.send_message(cid, "הכנס שם מלא:")
                steps[cid] = 'name'
    else:
                bot.send_message(cid, "הכנס שם לאיסוף:")
                steps[cid] = 'pickup_name'

def ask_quantity(cid):
    markup = types.InlineKeyboardMarkup()
    for i in range(1, 6):
        markup.add(types.InlineKeyboardButton(f"{i}", callback_data=f"quantity_{i}"))
    bot.send_message(cid, "בחר כמות:", reply_markup=markup)

def ask_delivery(cid):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("משלוח", callback_data='delivery'))
    markup.add(types.InlineKeyboardButton("איסוף", callback_data='pickup'))
    bot.send_message(cid, "בחר שיטה:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.chat.id in steps)
def collect_details(message):
    cid = message.chat.id
    step = steps[cid]
    text = message.text

    if step == 'name':
        user_data[cid]['name'] = text
        bot.send_message(cid, "הכנס כתובת מלאה:")
        steps[cid] = 'address'
    elif step == 'address':
        user_data[cid]['address'] = text
        bot.send_message(cid, "הכנס מספר טלפון:")
        steps[cid] = 'phone'
    elif step == 'phone':
        user_data[cid]['phone'] = text
        send_summary(cid)
        steps.pop(cid)
    elif step == 'pickup_name':
        user_data[cid]['name'] = text
        bot.send_message(cid, "הכנס מספר טלפון:")
        steps[cid] = 'pickup_phone'
    elif step == 'pickup_phone':
        user_data[cid]['phone'] = text
        send_summary(cid)
        steps.pop(cid)

def send_summary(cid):
    data = user_data.get(cid, {})
    username = f"@{bot.get_chat(cid).username}" if bot.get_chat(cid).username else f"ID: {cid}"
    price = int(data.get('price', 0)) * int(data.get('quantity', 1))

    summary = (
        f"\U0001F9FE *סיכום הזמנה:*\n"
        f"\U0001F464 לקוח: {username}\n"
        f"\U0001F4DE טלפון: {data.get('phone', '---')}\n"
        f"\U0001F4CD כתובת: {data.get('address', '---') if data.get('method') == 'משלוח' else 'איסוף עצמי'}\n"
        f"\U0001F4E6 מוצר: {data.get('product', '---')}\n"
        f"\U0001F522 כמות: {data.get('quantity', 1)}\n"
        f"\U0001F4B8 מחיר כולל: {price}₪\n"
        f"\U0001F69A שיטה: {data.get('method')}")

    bot.send_message(cid, summary, parse_mode="Markdown")
    bot.send_message(ADMIN_CHAT_ID, f"\U0001F4E5 הזמנה חדשה:\n{summary}", parse_mode="Markdown")

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