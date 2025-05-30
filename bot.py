import telebot
from telebot import types
from flask import Flask, request
import os

TOKEN = '7809342094:AAEivr0_RTMX6udxMPS8lVaNaEyepSv-rC4'
ADMIN_CHAT_ID = 7759457391

bot = telebot.TeleBot(TOKEN)
app = Flask(name)
user_data = {}

prices_map = {
    "medica_1": 400, "medica_2": 700, "medica_3": 1000,
    "greenhouse_5": 150, "greenhouse_10": 250, "greenhouse_20": 400,
    "boutique_5": 200, "boutique_10": 350, "boutique_20": 600,
    "moroccan_1": 1200, "moroccan_2": 2000,
    "and_beautiful_frozen_1": 300, "and_beautiful_frozen_2": 550,
    "and_beautiful_apple_1": 300, "and_beautiful_apple_2": 550,
    "and_beautiful_papaya_1": 300, "and_beautiful_papaya_2": 550,
    "and_beautiful_velvet_1": 300, "and_beautiful_velvet_2": 550,
    "and_beautiful_frootz_1": 300, "and_beautiful_frootz_2": 550,
    "and_beautiful_zkittlez_1": 300, "and_beautiful_zkittlez_2": 550,
    "and_beautiful_wedding_1": 300, "and_beautiful_wedding_2": 550
}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("איסוף עצמי", callback_data="pickup"))
    markup.add(types.InlineKeyboardButton("משלוח", callback_data="delivery"))
    bot.send_message(message.chat.id, "בחר שיטת קבלה:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["pickup", "delivery"])
def handle_method(call):
    user_data[call.from_user.id] = {"method": call.data}
    if call.data == "pickup":
        show_products(call.message)
    else:
        bot.send_message(call.message.chat.id, "הכנס את שמך:")
        bot.register_next_step_handler(call.message, get_name)

def get_name(message):
    user_data[message.from_user.id]["name"] = message.text
    bot.send_message(message.chat.id, "הכנס את הכתובת:")
    bot.register_next_step_handler(message, get_address)

def get_address(message):
    user_data[message.from_user.id]["address"] = message.text
    bot.send_message(message.chat.id, "הכנס את מספר הטלפון:")
    bot.register_next_step_handler(message, get_phone)

def get_phone(message):
    user_data[message.from_user.id]["phone"] = message.text
    show_products(message)

def show_products(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("שקיות רפואי", callback_data="medica"))
    markup.add(types.InlineKeyboardButton("חממה", callback_data="greenhouse"))
    markup.add(types.InlineKeyboardButton("בוטיק", callback_data="boutique"))
    markup.add(types.InlineKeyboardButton("חשיש", callback_data="moroccan"))
    markup.add(types.InlineKeyboardButton("וייפים בטעמים", callback_data="and_beautiful"))
    bot.send_message(message.chat.id, "בחר מוצר:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "medica")
def show_medica(call):
    user_data[call.from_user.id]["product"] = "שקיות רפואי"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("1 - 400₪", callback_data="medica_1"))
    markup.add(types.InlineKeyboardButton("2 - 700₪", callback_data="medica_2"))
    markup.add(types.InlineKeyboardButton("3 - 1000₪", callback_data="medica_3"))
    path = "images/medica.jpg"
    if os.path.exists(path):
        with open(path, 'rb') as photo:
            bot.send_photo(call.message.chat.id, photo, caption="בחר כמות:", reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, "בחר כמות:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["greenhouse", "boutique", "moroccan"])
def show_others(call):
    product_map = {
        "greenhouse": "חממה",
        "boutique": "בוטיק",
        "moroccan": "חשיש"
    }
    product = call.data
    user_data[call.from_user.id]["product"] = product_map[product]

    prices = {
        "greenhouse": [("5 - 150₪", "greenhouse_5"), ("10 - 250₪", "greenhouse_10"), ("20 - 400₪", "greenhouse_20")],
        "boutique": [("5 - 200₪", "boutique_5"), ("10 - 350₪", "boutique_10"), ("20 - 600₪", "boutique_20")],
        "moroccan": [("1 - 1200₪", "moroccan_1"), ("2 - 2000₪", "moroccan_2")]
    }

    images = {
        "greenhouse": "images/greenhouse.jpg",
        "boutique": "images/boutique.jpg",
        "moroccan": "images/moroccan.jpg"
    }

    markup = types.InlineKeyboardMarkup()
    for label, cb in prices[product]:
        markup.add(types.InlineKeyboardButton(label, callback_data=cb))

    path = images.get(product)
    if path and os.path.exists(path):
        with open(path, 'rb') as photo:
            bot.send_photo(call.message.chat.id, photo, caption="בחר כמות:", reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, "בחר כמות:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "and_beautiful")
def handle_vapes(call):
    user_data[call.from_user.id]["product"] = "וייפים בטעמים"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Frozen grapes 🍇", callback_data="flavor_frozen"))
    markup.add(types.InlineKeyboardButton("Apple jam 🍏", callback_data="flavor_apple"))
    markup.add(types.InlineKeyboardButton("Papaya 🍑", callback_data="flavor_papaya"))
    markup.add(types.InlineKeyboardButton("Blu velvet 🫐", callback_data="flavor_velvet"))
    markup.add(types.InlineKeyboardButton("Blu frootz ❄️", callback_data="flavor_frootz"))
    markup.add(types.InlineKeyboardButton("LA Zkittlez 🍬", callback_data="flavor_zkittlez"))
    markup.add(types.InlineKeyboardButton("Wedding CK", callback_data="flavor_wedding"))

    path = "images/and_beautiful.MP4"
    if os.path.exists(path):
        with open(path, 'rb') as video:
            bot.send_video(call.message.chat.id, video, caption="בחר טעם:", reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, "בחר טעם:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("flavor_"))
def handle_flavor(call):
    flavor = call.data.replace("flavor_", "")
    user_data[call.from_user.id]["flavor"] = flavor
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("1 - 300₪", callback_data=f"vape_{flavor}_1"))
    markup.add(types.InlineKeyboardButton("2 - 550₪", callback_data=f"vape_{flavor}_2"))
    bot.send_message(call.message.chat.id, "בחר כמות:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("vape_"))
def handle_vape_quantity(call):
    _, flavor, qty = call.data.split("_")
    key = f"and_beautiful_{flavor}_{qty}"
    user_data[call.from_user.id]["selection"] = key
    user_data[call.from_user.id]["flavor"] = flavor
    user_data[call.from_user.id]["quantity"] = qty
    send_summary(call.message)

@bot.callback_query_handler(func=lambda call: call.data in prices_map)
def handle_quantity(call):
    user_data[call.from_user.id]["selection"] = call.data
    user_data[call.from_user.id]["quantity"] = call.data.split("_")[-1]
    send_summary(call.message)

def send_summary(message):
    data = user_data.get(message.from_user.id, {})
    method = data.get("method", "-")
    name = data.get("name", "-") if method == "delivery" else message.from_user.first_name
    address = data.get("address", "-") if method == "delivery" else "-"
    phone = data.get("phone", "-")
    product = data.get("product", "None")
    flavor = data.get("flavor", "ללא")
    quantity = data.get("quantity", "-")
    selection_key = data.get("selection", "-")
    price = prices_map.get(selection_key, "-")

    summary = (
        "📦 התקבלה הזמנה:\n"
        f"שיטה: {'איסוף עצמי' if method == 'pickup' else 'משלוח'}\n"
        f"שם: {name}\n"
        f"כתובת: {address}\n"
        f"טלפון: {phone}\n"
        f"מוצר: {product}\n"
        f"טעם: {flavor}\n"
        f"כמות: {quantity}\n"
        f"סכום לתשלום: {price} ₪\n"
        f"יוזר: @{message.from_user.username or 'אין'}"
    )

bot.send_message(message.chat.id, "✅ הזמנתך התקבלה!\nתודה שבחרת במיידי פראם 🫶")
    bot.send_message(ADMIN_CHAT_ID, summary)

    if method == "pickup":
        pickup_summary = (
            "🛍 הזמנת איסוף:\n"
            f"שם: {name}\n"
            f"טלפון: {phone}\n"
            f"מוצר: {product}\n"
            f"כמות: {quantity}"
        )
        bot.send_message(ADMIN_CHAT_ID, pickup_summary)

@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@app.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://telegram-bot-z2i5.onrender.com/' + TOKEN)
    return "Webhook set!", 200

if name == 'main':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))