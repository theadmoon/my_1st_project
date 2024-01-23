from telebot import TeleBot
import info_bot

# вставь сюда свой токен
token = "6692081952:AAFi4pdTMmXpq-G1pCCdUwbu5Rn8il-Eeh4"

# подключаемся к телеграму
bot = telebot.TeleBot(token=token)

# вставь сюда свой chat_id
#chat_id = 168751776

help_message = \
''' Я умею:
/help - помощь, список возможностей
/about - информация о данном боте
/portfolio - список моих работ
/contacts - контакты для связи
Название проекта можно ввести текстом'''

@bot.message_handler(commands=['start'])
def bot_start(message):
    bot.send_message(message.chat.id,
                     text=f'Hello,{message.from_user.first_name}! ' + help_message)

@bot.message_handler(commands=['help'])
def bot_help(message):
    bot.send_message(message.chat.id, text=help_message)

@bot.message_handler(commands=['about'])
def bot_about(message):
    bot.send_message(message.chat.id, text=info_bot.about_me)
    bot.send_photo(message.chat.id,open('image3.jpg', 'rb'))

    #with file = open (filename, 'rb') r/w
    #    data = file.read()
    #bot.send_photo(message.chat.id, img_url, description)
    #bot.send_voice(message.chat.id, open('media/voice.ogg', 'rb'))

@bot.message_handler(commands=['contacts'])
def bot_contacts(message):
    bot.send_message(message.chat.id, text=info_bot.contacts, parse_mode='expression expected')

@bot.message_handler(commands=['portfolio'])
def bot_portfolio(message):
    bot.send_message(message.chat.id, text=info_bot.show_projects())

def is_in_projects(message):
    for project in info_bot.projects:
        if project.lowever() in message.text.lowever():
            message.text = project
            return True
    return False
@bot.message_handler(content_types=['text'])
def bot_projects(message):
    description = info_bot.describe_project(message.text)

    if description:
        bot.send_message(message.chat.id, text=description)
    else:
        bot.send_message(message.chat.id, text="Нет такого проекта, проверь написание. "
                                               "Список проектов доступен при вызове команды /portfolio")
bot.polling()