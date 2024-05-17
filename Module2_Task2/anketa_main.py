import json
import os

import telebot
from questions import characters, questions, welcome_message
from telebot import types

TOKEN = "6692081952:AAFi4pdTMmXpq-G1pCCdUwbu5Rn8il-Eeh4"
bot = telebot.TeleBot(TOKEN)

def load_user_data():
    with open("user_data.json", "r") as file:
        return json.load(file)

def save_user_data(user_data):
    with open("user_data.json", "w") as file:
        json.dump(user_data, file)

# Структура для хранения данных пользователя
# Считываем данные из файла, если файл существует
if os.path.exists("user_data.json"):
    user_data = load_user_data()
else:
    user_data = {}


# Обработчик команды /start
@bot.message_handler(commands=["start"])
def start_survey(message):
    # Инициализируем данные пользователя
    # user_data[message.chat.id] = {character: 0 for character in characters}
    user_data[message.chat.id] = {}  # создание вложенного словаря для запоминания состояния очков персонажей пользователя
    for character in characters:
        user_data[message.chat.id][character] = 0  # создание ключей персонажей и их значений в 0

    user_data[message.chat.id]["question_index"] = 0 # создание ключа для запоминания номера вопроса и его значения в 0

    # Отправляем приветственное сообщение
    bot.send_message(message.chat.id, welcome_message)
    send_question(message.chat.id) # Вызов функции отправки вопроса

    # Сохраняем данные пользователя
    save_user_data(user_data)


# Функция отправки вопроса
def send_question(chat_id):
    question_index = user_data[chat_id]["question_index"]

    # Получаем текст вопроса и варианты ответа
    question_data = questions[question_index] # словарь вопросов по индексу вопроса (элемент списка)
    question_text = question_data["question"] # текст вопроса по ключу question
    options = question_data["answers"] # словарь ответов по ключу answers

    # Создаем клавиатуру с вариантами ответа и отправляем вопрос через метод bot.send_message
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True) # one_time_keyboard=True скрывает клавиатуру после того, как пользователь выберет один из вариантов ответа.
    # resize_keyboard=True позволяет автоматически изменять размер клавиатуры в зависимости от количества кнопок.

    for text in options: # Цикл проходится по вариантам ответа, options - словарь текстовых вариантов ответа.
        markup.add(text) # добавляет каждый вариант в созданную клавиатуру
    bot.send_message(chat_id, question_text, reply_markup=markup) # Отправление сообщения с текстом вопроса (question_text) и прикрепленной к нему созданной клавиатурой ответов (reply_markup=markup).


# Обработчик получения сообщения
#def always_true(message):
#    return True
@bot.message_handler(func=lambda message: True) # @bot.message_handler(func=always_true) # @bot.message_handler(content_type= ['text'], func=handle_answer)
def handle_answer(message):
    # Проверяем, что пользователь начал анкету
    if message.chat.id not in user_data:
        bot.send_message(message.chat.id, "Пожалуйста, начните анкету с помощью команды /start")
        return

    # Получаем индекс текущего вопроса пользователя
    question_index = user_data[message.chat.id]["question_index"]
    question_data = questions[question_index] # вопрос по индексу в списке вопросов
    options = question_data["answers"] # словарь ответов по ключу answers

    # Проверяем, что ответ соответствует одному из предложенных вариантов
    #selected_option = options.get(message.text)
    #if selected_option is None:
    #    bot.send_message(message.chat.id, "Пожалуйста, выберите один из предложенных вариантов.")
    #    return
    if message.text not in options:
        bot.send_message(message.chat.id, "Пожалуйста, выберите один из предложенных вариантов.")
        return

    selected_option = options[message.text] # получение словаря вариантов ответов со словарём весов персонажей в переменную selected_option

    # Обновляем счет пользователя
    for character, score in selected_option.items():
        user_data[message.chat.id][character] += score # добавление очков персонажей в файл текущего пользователя по ключу character

    # Переходим к следующему вопросу или отправляем результат
    user_data[message.chat.id]["question_index"] += 1 # увеличение счётчика вопроса пользователя
    if user_data[message.chat.id]["question_index"] < len(questions):
        send_question(message.chat.id)
    else:
        send_result(message.chat.id)

    # Сохраняем данные пользователя
    save_user_data(user_data)


# Функция отправки результата
def send_result(chat_id):
    # Получаем очки пользователя
    # scores = {character: score for character, score in user_data[chat_id].items() if character != "question_index"}
    scores = {}
    for character, score in user_data[chat_id].items():
        if character != "question_index":
            scores[character] = score

    # Определяем персонажа с наибольшим количеством очков
    max_character = max(scores) # key=scores.get

    # Получаем описание персонажа
    description, image_name = characters[max_character]
    caption_message = f"Ваша предрасположенность к обучению: {max_character}\n{description}"

    # Считываем картинку персонажа и отправляем результат
    with open(image_name, "rb") as image:
        bot.send_photo(chat_id, image, caption=caption_message)

    # Удаляем данные пользователя после завершения анкеты
    del user_data[chat_id]

    # Сохраняем изменение
    save_user_data(user_data)


# Запуск бота
bot.polling(non_stop=True)