import json
import os
import telebot
from telebot import types
from myfinallocations import locations_data

TOKEN = "6692081952:AAFi4pdTMmXpq-G1pCCdUwbu5Rn8il-Eeh4"
bot = telebot.TeleBot(TOKEN)

def load_user_data():
    try:
        with open("user_data.json", "r") as file:
            return json.load(file)
    except:
        return {}

def save_user_data(user_data):
    with open("user_data.json", "w") as file:
        json.dump(user_data, file)

if os.path.exists("user_data.json"):
    user_data = load_user_data()
else:
    user_data ={}
@bot.message_handler(commands=["start"])
def start_quest(message):
    global user_data
    if str(message.chat.id) in user_data and user_data[str(message.chat.id)] not in ["entrance-2.1", "entrance-3.1", "entrance-3.2"]:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add("Начало")
        markup.add("Продолжить")
        bot.send_message(message.chat.id, "Желаете продолжить или начать заново?", reply_markup=markup)
    else:
        user_data[str(message.chat.id)]={"location": "start"}
        send_location(str(message.chat.id))
def send_location(chat_id):
    current_location = user_data[str(chat_id)]["location"]
    location_data = locations_data[current_location]
    description = location_data["description"]
    actions = location_data["actions"]
    picture_path = location_data["picture"]

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for action_text in actions:
        markup.add(action_text)

    with open(picture_path, "rb") as photo:
        bot.send_photo(chat_id, photo)
    bot.send_message(chat_id, description, reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_answer(message):
    global user_data
    chat_id = message.chat.id
    if str(chat_id) not in user_data:
        bot.send_message(chat_id, "Для запуска квеста используйте команду /start")
        return
    if message.text == "Начало":
        user_data[str(chat_id)]["location"] ="start"
        send_location(str(chat_id))
    elif message.text == "Продолжить":
        current_location = user_data[str(chat_id)]["location"]
        send_location(str(chat_id))
    current_location = user_data[str(chat_id)]["location"]
    actions = locations_data[current_location]["actions"]
    if message.text not in actions:
        bot.send_message(chat_id, "Введите один из предложенных вариантов.")
        return
    user_data[str(chat_id)]["location"] = actions[message.text]
    send_location(str(chat_id))

    save_user_data(user_data)

bot.polling(non_stop=True)
