import telebot
from telebot import types
from flask import Flask, request
import os

TOKEN = '7809342094:AAEivr0_RTMX6udxMPS8lVaNaEyepSv-rC4'
ADMIN_CHAT_ID = 7759457391

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
user_data = {}

prices_map = {
    "medica_1": 400, "medica_2": 700, "medica_3": 1000,
    "greenhouse_5": 150, "greenhouse_10": 250, "greenhouse_20": 400,
    "boutique_5": 200, "boutique_10": 350, "boutique_20": 600,
    "and_beautiful_strawberry": 300, "and_beautiful_grape": 300, "and_beautiful_mango": 300,
    "moroccan_1": 1200, "moroccan_2": 2000
}

# Start
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("איסוף עצמי", callback_data="pickup"))
    markup.add(types.InlineKeyboardButton("משלוח", callback_data="delivery"))
    bot.send_message(message.chat.id, "בחר שיטת קבלה:", reply_markup=markup)

# Method chosen
@bot.callback_query_handler(func=lambda call: call.data in ["pickup", "delivery"])
def handle_method(call):
    user_data[call.from_user.id] = {"method": call.data}
    if call.data == "pickup":
        show_products(call.message)
    else:
        bot.send_message(call.message.chat.id, "הכנס את שמך:")
        bot.register_next_step_handler(call.message, get_name)

# Customer details
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

# Show main product categories
def show_products(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("שקיות רפואי", callback_data="medica"))
    markup.add(types.InlineKeyboardButton("חממה", callback_data="greenhouse"))
    markup.add(types.InlineKeyboardButton("בוטיק", callback_data="boutique"))
    markup.add(types.InlineKeyboardButton("וייפים בטעמים", callback_data="and_beautiful"))
    markup.add(types.InlineKeyboardButton("חשיש", callback_data="moroccan"))
    bot.send_message(message.chat.id, "בחר מוצר:", reply_markup=markup)

# Handle regular products
@bot.callback_query_handler(func=lambda call: call.data in ["medica", "greenhouse", "boutique", "moroccan"])
def show_prices(call):
    product = call.data
    user_data[call.from_user.id]["product"] = product

    images = {
        "medica": "images/medica.jpg",
        "greenhouse": "images/greenhouse.jpg",
        "boutique": "images/boutique.jpg",
        "moroccan": "images/moroccan.jpg"
    }

    prices = {
        "medica": [("1 - 400₪", "medica_1"), ("2 - 700₪", "medica_2"), ("3 - 1000₪", "medica_3")],
        "greenhouse": [("5 - 150₪", "greenhouse_5"), ("10 - 250₪", "greenhouse_10"), ("20 - 400₪", "greenhouse_20")],
        "boutique": [("5 - 200₪", "boutique_5"), ("10 - 350₪", "boutique_10"), ("20 - 600₪", "boutique_20")],
        "moroccan": [("1 - 1200₪", "moroccan_1"), ("2 - 2000₪", "moroccan_2")]
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

# Quantity chosen
@bot.callback_query_handler(func=lambda call: call.data in prices_map)
def handle_quantity(call):
    user_data[call.from_user.id]["selection"] = call.data
    send_summary(call.message)
# Handle vape flavors
@bot.callback_query_handler(func=lambda call: call.data == "and_beautiful")
def handle_vapes(call):
    user_data[call.from_user.id]["product"] = "and_beautiful"

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("תות", callback_data="flavor_strawberry"))
    markup.add(types.InlineKeyboardButton("ענבים", callback_data="flavor_grape"))
    markup.add(types.InlineKeyboardButton("מנגו", callback_data="flavor_mango"))

    path = "images/and_beautiful.MP4"
    if os.path.exists(path):
        with open(path, 'rb') as video:
            bot.send_video(call.message.chat.id, video, caption="בחר טעם:", reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, "בחר טעם:", reply_markup=markup)

# Flavor chosen
@bot.callback_query_handler(func=lambda call: call.data.startswith("flavor_"))
def handle_flavor(call):
    flavor = call.data.replace("flavor_", "")
    user_data[call.from_user.id]["flavor"] = flavor
    user_data[call.from_user.id]["selection"] = f"and_beautiful_{flavor}"
    bot.send_message(call.message.chat.id, "הזן כמות:")
    bot.register_next_step_handler(call.message, get_quantity)

# Manual quantity input
def get_quantity(message):
    user_data[message.from_user.id]["quantity"] = message.text
    send_summary(message)

# Send summary to user and admin
def send_summary(message):
    data = user_data.get(message.from_user.id, {})
    method = data.get("method", "-")
    name = data.get("name", "-") if method == "delivery" else "-"
    address = data.get("address", "-") if method == "delivery" else "-"
    phone = data.get("phone", "-") if method == "delivery" else "-"
    product = data.get("product", "None")
    flavor = data.get("flavor", "ללא")
    quantity = data.get("quantity", "-") if "quantity" in data else data.get("selection", "-").split("_")[-1]
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

    bot.send_message(message.chat.id, summary)
    bot.send_message(ADMIN_CHAT_ID, summary)

# --- Flask Routes for Render ---
@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@app.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://your-app-name.onrender.com/' + TOKEN)  # שנה ל-URL שלך
    return "Webhook set!", 200

if __name__ == '__main__' :
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))