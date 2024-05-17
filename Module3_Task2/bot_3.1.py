import json
import logging
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup
from config import TOKEN, MAX_TOKENS
from gpt import GPT


gpt = GPT()

bot = TeleBot(TOKEN)
MAX_LETTERS = MAX_TOKENS

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="log_file.txt",
    filemode="w",
)
logging.basicConfig(level=logging.INFO)

def save_to_json():
    with open('users_history.json', 'w', encoding='utf-8') as f:
        json.dump(users_history, f, indent=2, ensure_ascii=False)


def load_from_json():
    # noinspection PyBroadException
    try:
        with open('users_history.json', 'r+', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        data = {}

    return data
users_history = load_from_json()

# Словарик для хранения задач пользователей и ответов GPT

# Стираем данные для предыдущего города
def remove_previous_from_json():
# load JSON data from file
    with open('users_history.json', 'r') as file:
        data = json.load(file)
# key to remove
    key_to_remove = "user_id"
# checking if the key exists before removing
    if key_to_remove in data:
        removed_value = data.pop(key_to_remove)
        print(f"Removed key '{key_to_remove}' with value: {removed_value}")
# saving the updated JSON data back to the file
    with open('users_history.json', 'w') as file:
        json.dump(data, file, indent=2)

# Функция для создания клавиатуры с нужными кнопочками
def create_keyboard(buttons_list):
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons_list)
    return keyboard

# Приветственное сообщение /start
@bot.message_handler(commands=['start'])
def start(message):
    logging.info(f"User {message.from_user.id} pressed /start")
    user_name = message.from_user.first_name
    bot.send_message(message.chat.id,
                     text=f"Привет, {user_name}! Я бот-помощник для обзора аллергенной обстановки!\n"
                          f"Ты можешь прислать название города, а я постараюсь сообщить какие там сейчас риски.\n"
                          "Иногда ответы получаются слишком длинными - в этом случае ты можешь попросить продолжить.",
                     reply_markup=create_keyboard(["/solve_task", '/help']))
    bot.register_next_step_handler(message, proccess_user_question)
                                   # lambda m: bot.send_message(m.chat.id, f"Вы ввели: {m.text}"))
def proccess_user_question(message):
    # здесь проверяем что пришло, реальный вопрос или нажали кнопку
    logging.info(f" message.text = {message.text} in process_user_questiom")
    while message.text and message.text != '/solve_task':
        return support(message)
    return solve_task(message)


# Создание отчета логов /debug
@bot.message_handler(commands=['debug'])
def send_logs(message):
    with open("log_file.txt", "rb") as f1:
        bot.send_document(message.chat.id, f1)

# Команда /help
@bot.message_handler(commands=['help'])
def support(message):
    logging.info(f"User {message.from_user.id} pressed /help")
    bot.send_message(message.from_user.id,
                     text="Чтобы получить обзор аллергенной обстановки: нажми /solve_task, а затем укажи город",
                     reply_markup=create_keyboard(["/solve_task"]))

# фильтр для обработки кнопочки "Завершить решение"



# Команда /solve_task и регистрация функции get_promt() для обработки любого следующего сообщения от пользователя
@bot.message_handler(commands=['solve_task'])
def solve_task(message):
    logging.info(f"User {message.from_user.id} pressed /solve_task")
    bot.send_message(message.chat.id, "Укажи город, для которого уточняем аллерго риски:")
    bot.register_next_step_handler(message, get_promt)


# Фильтр для обработки кнопочки "Продолжить решение"
def continue_filter(message):
    logging.info(f"User {message.from_user.id} pressed Продолжить решение")
    button_text = 'Продолжить решение'
    return message.text == button_text

def end_filter(message):
    logging.info(f"User {message.from_user.id} pressed Завершить решение")
    button_text = 'Завершить решение'
    return message.text == button_text

# Получение задачи от пользователя или продолжение решения
@bot.message_handler(func=continue_filter)
def get_promt(message):
    logging.info(f"User {message.from_user.id} запустил get_promt")
    user_id = str(message.from_user.id)  # ВАЖНО!
    logging.info(f"User {message.from_user.id} имеет user_id {user_id}")

#   Проверка на тип сообщения (текст, картинка, видео и тд). Если это НЕ текст - сообщение об ошибке пользователю,

    if not message.text:
        logging.info(f"User {message.from_user.id} ввел не текст")
        bot.send_message(user_id, "Необходимо отправить именно текстовое сообщение")
        # Cледующее сообщение пользователя попадает в эту же функцию - get_promt()
        bot.register_next_step_handler(message, get_promt)
        return

    # Получаем текст сообщения от пользователя
    logging.info(f"User {message.from_user.id} значение message.text {message.text}")
    user_request = message.text
    logging.info(f"User {message.from_user.id} значение user_request {user_request}")


    # if len(user_request) >= MAX_TOKENS:
    #     bot.send_message(user_id, "Запрос превышает количество символов\nИсправь запрос")
    #     bot.register_next_step_handler(message, get_promt)
    #     return
    if user_request == "Завершить решение":
        logging.info(f"User {message.from_user.id} нажал завершить решение, начало get_promt")
        end_task(message)
    # Проверка задачи пользователя на количество токенов. Если количество символов больше - сообщение об ошибке пользователю
    logging.info(f"gpt.count_tokens(user_request) = {gpt.count_tokens(user_request)}")
    if gpt.count_tokens(user_request) >= gpt.MAX_TOKENS:
        logging.info(f"User {message.from_user.id} сработала проверка MAX_TOKENS")
        bot.send_message(user_id, "Запрос превышает количество символов\nИсправь запрос")
        bot.register_next_step_handler(message, get_promt)
        return

    # Проверка: если у пользователя нет начатой задачи, тогда ее нужно начать
    if user_id not in users_history or users_history[user_id] == {}:
        if user_request == "Продолжить решение":
            logging.info(f"User {message.from_user.id} pressed продолжить решение при проверке users_history[user_id]")
            bot.send_message(message.chat.id, "Кажется, вы еще не задали вопрос.")
            bot.register_next_step_handler(message, get_promt)
            return
        # Сохраняем промт пользователя и начало ответа GPT в словарик users_history
        users_history[user_id] = {
            'system_content': ("Ты бот, с профессиональными знаниями в области аллергии на пыльцу растений и возвращающий ответ в виде отчета об аллергенной обстановке в конкретной локации."
                             "Ты обязательно должен использовать информацию с сайта https://pollen.club"
                             "Опиши аллергенную обстановку для орешника и ольхи для заданной местности и сообщи текущий уровень аллергенной опасности для этих аллергенов по шкале от 1 до 10."),
                'user_content': user_request,
                'assistant_content': "Пишем отчет об актуальных рисках аллергии на пыльцу: "
        }
        save_to_json()
        logging.info(f"users_history[user_id]['user_content'] = {users_history[user_id]['user_content']}")
    # Пока что ответом от GPT будет любой текст, просто придумай его)
    # answer = "Позже здесь будет реальное решение, а пока что так :)"
    logging.info(f"users_history[user_id] = {users_history[user_id]}")
    prompt = gpt.make_promt(users_history[user_id])
    logging.info(f" prompt в gpt = {prompt}")
    resp = gpt.send_request(prompt)
    logging.info(f"запрос в gpt = {resp}")
    logging.info(f"resp.json() = {resp.json()}")
    if resp.json()['choices'][0]['message']['content'] != '':
        answer = resp.json()['choices'][0]['message']['content']
        logging.info(f"answer IN choices in resp.json() = {answer}")
    else:
        answer = (f"Обзор аллергенной обстановки для локации {users_history[user_id]['user_content']} подошел к концу.\n"
                  f" Спасибо, что воспользовались нашим сервисом!")
        logging.info(f"answer if NOT choices in resp.json() = {answer}")
        end_task(message)
        # solve_task(message)
    #return answer
    logging.info(f"answer = resp.json()['choices'][0]['message']['content'] = {answer}")
    bot.register_next_step_handler(message, get_promt)
    #   return
        #users_history[user_id] = {}
        #answer = "завершить решение"
    logging.info(f"answer (завершить решение) = {answer}")
        #end_task(message)

        # Дописываем этот ответ от GPT к предыдущему ответу GPT
    #logging.info(f"users_history[user_id]["assistant_content"] = {users_history[user_id]["assistant_content"]}")
    logging.info(f"answer = resp.json()['choices'][0]['message']['content'] = {answer}")
    logging.info(f"User {message.from_user.id} проверка user_ID")
    #try:
    users_history[user_id]["assistant_content"] += answer
    #except KeyError:
    #    users_history[user_id] = {}
        #end_task(message)
    save_to_json()

    # Отправляем полный ответ пользователю
    # Добавляем кнопки "продолжить решение" и "завершить решение".
    # Продолжить решение - пользователь просит GPT дописать ответ к текущей задаче
    # Завершить решение - решение задачи прекращается, все предыдущие сообщения удаляются из истории пользователя
    keyboard = create_keyboard(["Продолжить решение", "Завершить решение"])
    bot.send_message(message.chat.id, answer, reply_markup=keyboard)

@bot.message_handler(func=end_filter)
def end_review(message):
    logging.info(f"User {message.from_user.id} находится в end_review")
    #bot.send_message(user_id, "Текущее решение завершено")
    bot.send_message(message.chat.id,
                     text=f"Заканчиваем обзор.",
                     reply_markup=create_keyboard(["/end"]))

@bot.message_handler(commands=['end'])
#@bot.message_handler(func=end_review)
#@bot.message_handler(content_types=['text'], func=lambda message: message.text.lower() == "завершить решение")
def end_task(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Текущее решение завершено")
    logging.info(f"users_history = {users_history}  ДО в end_task")
    users_history[user_id] = {}
    #open('users_history.json', 'w').close()
    #users_history[user_id].clear()
    save_to_json()
    #load_from_json()
    #remove_previous_from_json()
    logging.info(f"users_history = {users_history} ПОСЛЕ в end_task")
    start(message)
bot.polling()
