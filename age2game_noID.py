import telebot

# Создаём бота
API_TOKEN = '6692081952:AAFi4pdTMmXpq-G1pCCdUwbu5Rn8il-Eeh4'
bot = telebot.TeleBot(API_TOKEN)

# Изначально возраст неизвестен, обозначим это как -1
age = -1

# Начало работы, спрашиваем возраст
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я умею рекомендовать игры.")
    bot.send_message(message.chat.id, "Пожалуйста, скажи, сколько тебе лет?")

# Если возраст уже указан, рекомендуем игру
@bot.message_handler(commands=['game'])
def game(message):
    # age == -1 значит, что возраст не указан
    if age == -1:
        bot.send_message(message.chat.id, "Пожалуйста, пришли сначала свой возраст.")
    elif age < 13:
        bot.send_message(message.chat.id, "Minecraft")
    elif 13 <= age < 18:
        bot.send_message(message.chat.id, "Baba Is You")
    else:
        bot.send_message(message.chat.id, "The Stanley Parable")

# Запоминаем присланный возраст
@bot.message_handler()
def save_age(message):
    # Проверяем, что возраст - число
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "Пожалуйста, пришли свой возраст цифрами.")
    else:
        # Запоминаем присланный возраст в глобальную переменную `age`, объявленную в начале программы
        global age
        age = int(message.text)
        bot.send_message(message.chat.id, "Отлично, я запомнил! Теперь можешь использовать команду /game")

# Запускаем бота
bot.polling()