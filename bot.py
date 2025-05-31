import telebot
from telebot import types
from flask import Flask, request
import os

TOKEN = '7809342094:AAHLYD5GM1lZFBAR20oJXjdZZCtAEoTdFnc'
ADMIN_CHAT_ID = 7759457391
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

user_data = {}

# Prices
prices = {
    'greenhouse_5': 150, 'greenhouse_10': 250, 'greenhouse_20': 400,
    'vape_1': 300, 'vape_2': 550,
    'boutique_1': 1200, 'boutique_2': 2000,
    'medica_1': 400, 'medica_2': 700, 'medica_3': 1000
}

# Start command
@bot.message_handler(commands=['start'])
def start(message):
    user_data[message.from_user.id] = {}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('חשיש', 'וייפים')
    markup.row('בוטיק', 'חממה', 'שקיות')
    bot.send_message(message.chat.id, 'שלום וברוך הבא למיידי פארם – הבית של הרפואי 🌿', reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text in ['חממה', 'וייפים', 'חשיש', 'בוטיק', 'שקיות'])
def handle_menu(message):
    choice = message.text
    user_data[message.from_user.id]['category'] = choice

    if choice == 'חממה':
        send_image_with_options(message, 'greenhouse.jpg', [
            ('5 - 150₪', 'greenhouse_5'),
            ('10 - 250₪', 'greenhouse_10'),
            ('20 - 400₪', 'greenhouse_20')
        ])
    elif choice == 'וייפים':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        flavors = ['Frozen grapes', 'Apple jam', 'Papaya', 'Blu velvet', 'Blu frootz', 'LA Zkittlez', 'Wedding CK']
        for f in flavors:
            markup.add(f)
        send_video(message.chat.id, 'and_deautiful.Mp4', 'בחר טעם:', markup)
    elif choice == 'חשיש':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('1 - 1200₪', callback_data='boutique_1'))
        markup.add(types.InlineKeyboardButton('2 - 2000₪', callback_data='boutique_2'))
        send_video(message.chat.id, 'moroccan.Mp4', 'בחר כמות:', markup)
    elif choice == 'בוטיק':
        send_image_with_options(message, 'boutique.jpg', [
            ('1 - 400₪', 'medica_1'),
            ('2 - 700₪', 'medica_2'),
            ('3 - 1000₪', 'medica_3')
        ])
    elif choice == 'שקיות':
        show_bag_types(message)

def send_image_with_options(message, path, options):
    markup = types.InlineKeyboardMarkup()
    for text, cb in options:
        markup.add(types.InlineKeyboardButton(text, callback_data=cb))
    with open(f'images/{path}', 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption='בחר כמות:', reply_markup=markup)

def send_image(chat_id, path, caption):
    with open(f'images/{path}', 'rb') as photo:
        bot.send_photo(chat_id, photo, caption=caption)

def send_video(chat_id, path, caption, markup):
    with open(f'images/{path}', 'rb') as video:
        bot.send_video(chat_id, video, caption=caption, reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ['Frozen grapes', 'Apple jam', 'Papaya', 'Blu velvet', 'Blu frootz', 'LA Zkittlez', 'Wedding CK'])
def handle_vape_flavor(message):
    user_data[message.from_user.id]['flavor'] = message.text
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('1 - 300₪', callback_data='vape_1'))
    markup.add(types.InlineKeyboardButton('2 - 550₪', callback_data='vape_2'))
    bot.send_message(message.chat.id, 'בחר כמות:', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_selection(call):
    user_data[call.from_user.id]['selection'] = call.data
    bot.send_message(call.message.chat.id, 'איך תרצה לקבל את ההזמנה? איסוף או משלוח?')
    bot.register_next_step_handler(call.message, get_delivery_method)

def get_delivery_method(message):
    text = message.text.strip()
    if 'משלוח' in text:
        bot.send_message(message.chat.id, 'הכנס כתובת מלאה:')
        bot.register_next_step_handler(message, get_address)
    else:
        bot.send_message(message.chat.id, 'הכנס שם מלא:')
        bot.register_next_step_handler(message, get_name)
def get_address(message):
    user_data[message.from_user.id]['address'] = message.text
    bot.send_message(message.chat.id, 'הכנס שם מלא:')
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    user_data[message.from_user.id]['name'] = message.text
    bot.send_message(message.chat.id, 'הכנס מספר טלפון:')
    bot.register_next_step_handler(message, get_phone)

def get_phone(message):
    user_data[message.from_user.id]['phone'] = message.text
    send_summary(message)

def send_summary(message):
    data = user_data.get(message.from_user.id, {})
    flavor = data.get('flavor', '-')
    selection = data.get('selection', '-')
    price = prices.get(selection, '-')
    address = data.get('address', '-')
    name = data.get('name', '-')
    phone = data.get('phone', '-')
    category = data.get('category', '-')

    summary = (
        f"📦 הזמנה חדשה:\n"
        f"שם: {name}\n"
        f"טלפון: {phone}\n"
        f"כתובת: {address}\n"
        f"קטגוריה: {category}\n"
        f"טעם (אם קיים): {flavor}\n"
        f"פריט: {selection}\n"
        f"מחיר: {price} ₪\n"
        f"יוזר: @{message.from_user.username or 'אין'}"
    )

    bot.send_message(message.chat.id, '✅ הזמנתך התקבלה! תודה שבחרת במיידי פארם 🫶')
    bot.send_message(ADMIN_CHAT_ID, summary)

def show_bag_types(message):
    text = """מלאי שקיות חדש:
⭐️ סטיבה:
תל אביב, גין גאי, אלסקה, אולטרא סאוור, טי סי, סינרג׳י, מרמלדה, תכלת, מיאמי סקי, גי דיזל, אורגינל גי סי

⭐️ אינדיקה:
קוטון קנדי, פרפל גלו, מירקל אילן קוקיז, בלו מון, קריטיקל טיקס, תלתן סגול, בראוניז, הולנדי, הינדו, רפאל, גורילה גלו

⭐️ היברידי:
הי מאיה, סטרוננה, בלו אמרלד, בנגו, אטומטיק, וודינג סי קי"""
    with open('images/medica.jpg', 'rb') as img:
        bot.send_photo(message.chat.id, img, caption=text)

# Flask routes
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return '', 200

@app.route('/', methods=['GET'])
def index():
    return 'Bot is running', 200

if  __name__ == '__main__' :
     bot.remove_webhook()
     bot.set_webhook(url="https://telegram-bot-z2i5.onrender.com/7809342094:AAHLYD5GM1lZFBAR20oJXjdZZCtAEoTdFnc")
     port = int(os.environ.get('PORT', 5000))
     app.run(host='0.0.0.0', port=port)