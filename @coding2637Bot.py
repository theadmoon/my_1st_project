import telebot

# вставь сюда свой токен
token = "6692081952:AAFi4pdTMmXpq-G1pCCdUwbu5Rn8il-Eeh4"

# подключаемся к телеграму
bot = telebot.TeleBot(token=token)

# вставь сюда свой chat_id
chat_id = 168751776

# отправляем сообщение
bot.send_message(chat_id, "Я проснулся!")

@bot.message_handler(content_types=['text'])
def repeat_message(message): # Функция для обработки сообщений
      bot.send_message(message.chat.id, message.text) # Отправка ответа

bot.polling()

# Пример: обработка только текстовых и голосовых сообщений
@bot.message_handler(content_types=['text', 'audio'])
def handle_text_audio(message):
    pass # это ключевое слово можно использовать, чтобы Python не ругался на пустую функцию

# Пример: обработка только команд '/start' и '/help'
@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    pass


# Функция для фильтрации сообщений: возвращает True, если длина сообщения меньше 100
def check_message_len(message):
      return len(message.text) <= 100


# Пример: обработка сообщений по длине с нашей собственной функцией
# Будут обработаны только короткие сообщения

@bot.message_handler(func=check_message_len)
def handle_text_doc(message):
      pass

def filter_password(message):
    password = "хомяк"
    return password in message.text

@bot.message_handler(content_types=['text'], func = filter_password)
def say_hello(message):
    bot.send_message(message.chat.id, "Привет!")

bot.polling() 