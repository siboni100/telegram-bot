import telebot
from telebot import types
from flask import Flask, request
import os

TOKEN = '7809342094:AAGpLE7T5E-Spvd7Gzv7cpSDKTpf_HDpHAo'
ADMIN_CHAT_ID = 7759457391
GROUP_CHAT_ID = -1002639815887

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

bags = {
    'סטיבה': ['תל אביב', 'גין גאי', 'אלסקה', 'אולטרא סאוור', 'טי סי', 'סינרג׳י', 'מרמלדה', 'תכלת', 'מיאמי סקי', 'גי דיזל', 'אורגינל גי סי'],
    'אינדיקה': ['קוטון קנדי', 'פרפל גלו', 'מירקל אילן קוקיז', 'בלו מון', 'קריטיקל טיקס', 'תלתן סגול', 'בראוניז', 'הולנדי', 'הינדו', 'רפאל', 'גורילה גלו'],
    'היברידי': ['הי מאיה', 'סטרוננה', 'בלו אמרלד', 'בנגו', 'אטומטיק', 'וודינג סי קי']
}

@bot.message_handler(commands=['start'])
def start(message):
    cid = message.chat.id
    user_data[cid] = {}

    # כפתורי הקטגוריות שיופיעו עם התמונה
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("חשיש", callback_data='menu_hashish'))
    markup.add(types.InlineKeyboardButton("וייפים", callback_data='menu_and_beautiful.MP4'))
    markup.add(types.InlineKeyboardButton("בוטיק", callback_data='menu_boutique'))
    markup.add(types.InlineKeyboardButton("חממה", callback_data='menu_greenhouse'))
    markup.add(types.InlineKeyboardButton("שקיות רפואי", callback_data='menu_medica'))

    # שולח את התמונה יחד עם הכפתורים
    with open('images/photo_2025-06-02_00-51-05.jpg', 'rb') as photo:
        bot.send_photo(cid, photo, caption="ברוך הבא למיידי פארם, בחר קטגוריה:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    cid = call.message.chat.id
    data = call.data

    if data.startswith('menu_'):
        category = data.replace('menu_', '')
        if category == 'hashish':
            with open('images/moroccan.MP4', 'rb') as video:
                bot.send_video(cid, video)
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("1 = 1200₪", callback_data='moroccan_1'))
            markup.add(types.InlineKeyboardButton("2 = 2000₪", callback_data='moroccan_2'))
            bot.send_message(cid, "בחר כמות:", reply_markup=markup)

        elif category == 'and_beautiful.MP4':
            with open('images/and_beautiful.MP4', 'rb') as video:
                bot.send_video(cid, video)
            markup = types.InlineKeyboardMarkup()
            vape_flavors = ['Frozen grapes', 'Apple jam', 'Papaya', 'Blu velvet', 'Blu frootz', 'LA Zkittlez']
            for flavor in vape_flavors:
                markup.add(types.InlineKeyboardButton(flavor, callback_data=f'vape_flavor_{flavor}'))
            bot.send_message(cid, "בחר טעם:", reply_markup=markup)

        elif category == 'greenhouse':
            with open('images/greenhouse.jpg', 'rb') as photo:
                bot.send_photo(cid, photo)
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("5 גרם - 150₪", callback_data='greenhouse_5'))
            markup.add(types.InlineKeyboardButton("10 גרם - 250₪", callback_data='greenhouse_10'))
            markup.add(types.InlineKeyboardButton("20 גרם - 400₪", callback_data='greenhouse_20'))
            bot.send_message(cid, "בחר כמות:", reply_markup=markup)

        elif category == 'boutique':
            with open('images/boutique.jpg', 'rb') as photo:
                bot.send_photo(cid, photo)
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("5 = 200₪", callback_data='boutique_5'))
            markup.add(types.InlineKeyboardButton("10 = 350₪", callback_data='boutique_10'))
            markup.add(types.InlineKeyboardButton("20 = 650₪", callback_data='boutique_20'))
            bot.send_message(cid, "בחר כמות:", reply_markup=markup)

        elif category == 'medica':
            with open('images/medica.jpg', 'rb') as photo:
                bot.send_photo(cid, photo)
            markup = types.InlineKeyboardMarkup()
            for cat in bags:
                markup.add(types.InlineKeyboardButton(cat, callback_data=f'bag_type_{cat}'))
            bot.send_message(cid, "בחר סוג:", reply_markup=markup)

    elif data.startswith('vape_flavor_'):
    flavor_id = data.replace('vape_flavor_', '')

    # מיפוי מזהים לשמות טעמים אמיתיים
    flavor_names = {
        '1': 'Frozen grapes',
        '2': 'Apple jam',
        '3': 'Papaya',
        '4': 'Blu velvet',
        '5': 'Blu frootz',
        '6': 'LA Zkittlez'
    }

    # קבלת שם הטעם מהמילון
    flavor_name = flavor_names.get(flavor_id, '---')
    user_data[cid]['product'] = flavor_name
    user_data[cid]['type'] = 'וייפ'

    # בחירת כמות
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("1 = 300₪", callback_data='vape_1'))
    markup.add(types.InlineKeyboardButton("2 = 550₪", callback_data='vape_2'))
    bot.send_message(cid, "בחר כמות:", reply_markup=markup)


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

    elif data in prices:
        user_data[cid]['product'] = data
        user_data[cid]['price'] = prices[data]
        quantity = int(data.split('_')[-1])
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

def ask_delivery(cid):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("משלוח", callback_data='delivery'))
    markup.add(types.InlineKeyboardButton("איסוף עצמי", callback_data='pickup'))
    bot.send_message(cid, "בחר שיטת קבלת ההזמנה:", reply_markup=markup)

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
    chat = bot.get_chat(cid)
    username = f"@{chat.username}" if chat.username else f"ID: {cid}"
    price = int(data.get('price', 0)) * int(data.get('quantity', 1))

    summary = (
        f"📾 סיכום הזמנה:\n"
        f"👤 לקוח: {username}\n"
        f"📞 טלפון: {data.get('phone', '---')}\n"
        f"📍 כתובת: {data.get('address', '---') if data.get('method') == 'משלוח' else 'איסוף עצמי'}\n"
        f"🧃 קטגוריה: {data.get('type', '---')}\n"
        f"🍓 טעם/זן: {data.get('product', '---')}\n"
        f"🔢 כמות: {data.get('quantity', 1)}\n"
        f"💰 מחיר כולל: {price}₪\n"
        f"🚚 שיטה: {data.get('method', '---')}"
    )

    bot.send_message(cid, summary)
    bot.send_message(ADMIN_CHAT_ID, f"📩 הזמנה חדשה:\n{summary}")
    bot.send_message(cid, "תודה שבחרת במיידי פארם 🫶")

# פוסט עם כפתורים - שליחה ידנית
@bot.message_handler(commands=['post'])
def send_post(message):
    if message.chat.type == "private":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("Mike Tyson 💥", url="https://t.me/Mike_Tyson5"),
            types.InlineKeyboardButton("Doktor Gril 💥", url="https://t.me/doktorgril1"),
            types.InlineKeyboardButton("הבוט שלנו 💥", url="https://t.me/Pharma122_bot")
        )
        with open("images/photo_2025-06-01_03-29-19.jpg", "rb") as photo:
            bot.send_photo(
                chat_id=GROUP_CHAT_ID,
                photo=photo,
                caption="""🏋️‍♂️🔥 *הקבוצה הכי חזקה בדרום!*

לקוחות חוזרים *באש ובאהבה* ❤️‍🔥  
לא עוברים *לאף אחד* ❌  
נשארים *רק אצלנו* 🫡💪  
לקוחות גבוהים – ומפסוטים 😎🧠

⸻

🎯 כל סגירה – בול בפוני  
✅ כל בעיה – פתורה לך  
💎 המשלוחים שלנו – הכי טובים בעיר  
🎉 כל יום מבצעים חדשים

🌐 *אחד למעטפת – הכל במקום אחד*""", 
                parse_mode="Markdown",
                reply_markup=markup
            )

# ריצה עם Flask + webhook
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "ok", 200

@app.route("/")
def index():
    return "Hello from Miday Pharma bot!"

if __name__ == "__main__":
    # הגדרת webhook לכתובת הריצה שלך (החלף את ה-URL)
    WEBHOOK_URL =("https://telegram-bot-zzi5.onrender.com/7809342094:AAGpLE7T5E-Spvd7Gzv7cpSDKTpf_HDpHAo")
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
