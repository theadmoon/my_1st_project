
import telebot

# Создаём бота
API_TOKEN = '6692081952:AAFi4pdTMmXpq-G1pCCdUwbu5Rn8il-Eeh4'
bot = telebot.TeleBot(API_TOKEN)

# Изначально пользователей нет, пустой словарь
user_data = {}

# Начало работы, спрашиваем возраст
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я умею рекомендовать игры.")
    bot.send_message(message.chat.id, "Пожалуйста, скажи, сколько тебе лет?")

# Если возраст уже указан, рекомендуем игру
@bot.message_handler(commands=['game'])
def game(message):
    # Получаем `user_id` пользователя
    user_id = message.from_user.id

    # Проверяем, что user_id пользователя есть в словаре
    # Если нет -- просим прислать свой возраст
    if user_id not in user_data:
        bot.send_message(message.chat.id, "Пожалуйста, пришли сначала свой возраст.")
    elif user_data[user_id] < 13:
        bot.send_message(message.chat.id, "Minecraft")
    elif 13 <= user_data[user_id] < 18:
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
        # Получаем `user_id` пользователя
        user_id = message.from_user.id

        # Запоминаем присланный возраст в локальную переменную `age`
        age = int(message.text)
        # Сохраняем возраст пользователя в словарь по `user_id`
        user_data[user_id]['age'] = age
        # Сохраняем имя пользователя в словарь по `user_id`
        user_data[user_id]['name'] = message.from_user.first_name

        bot.send_message(message.chat.id, "Отлично, я запомнил! Теперь можешь использовать команду /game")

# Запускаем бота
bot.polling()

'''Словари с набором значений
Иногда задачи требуют хранения большого количества данных. Это может быть возраст, имя или, например, количество использований бота. Тут тоже помогут словари, только вместо одного значения, как в прошлом примере, нужно сохранить набор значений. Для этого также удобно использовать словарь — можно дать явное название каждому из значений, чтобы не запутаться, например, age и name:
user_data = {
    123456789: {"age": 25, "name": "Анфиса"},
    987654321: {"age": 30, "name": "Кирилл"}
}
Теперь по каждому пользователю есть не только одно значение, но целый словарь с данными. Так можно собрать сколько угодно информации о пользователе, просто добавляя её в словарик.
Вот как можно это реализовать:
Создаём для каждого нового пользователя пустой словарь после команды /start:
 if user_id not in user_data:
         user_data[user_id] = {}

Записываем в этот словарь возраст, указанный пользователем:
 user_data[user_id]['age'] = age

При желании добавляем другую инфу. Например, имя:
 user_data[user_id]['name'] = message.from_user.first_name'''
