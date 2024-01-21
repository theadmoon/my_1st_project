import telebot

# вставь сюда свой токен
token = "6692081952:AAFi4pdTMmXpq-G1pCCdUwbu5Rn8il-Eeh4"

# подключаемся к телеграму
bot = telebot.TeleBot(token=token)

# вставь сюда свой chat_id
chat_id = 168751776


def filter_password(message):
    password = "привет"
    return password in message.text

@bot.message_handler(content_types=['text'], func = filter_password)
def say_hello(message):
    bot.send_message(message.chat.id, "Привет!")

def filter_password1(message):
    password = "пока"
    return password in message.text

@bot.message_handler(content_types=['text'], func = filter_password1)
def say_hello(message):
    bot.send_message(message.chat.id, "Прощай!")

bot.polling()