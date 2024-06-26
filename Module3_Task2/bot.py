import json
import logging
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup
from config import TOKEN, MAX_TOKENS
from gpt import GPT
from database import create_db, create_table, DB_NAME, execute_query, update_row_value

bot = TeleBot(TOKEN)
MAX_LETTERS = MAX_TOKENS
gpt = GPT()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="log_file.txt",
    filemode="w",
)
logging.basicConfig(level=logging.INFO)

# Словарь для хранения задач пользователей и ответов GPT
users_history = {}
# Словарь для хранения текущего выбора пользователем предмета и уровня
current_options = {}
create_db(DB_NAME)
create_table('users')

# Создание отчета логов /debug
@bot.message_handler(commands=['debug'])
def send_logs(message):
    with open("log_file.txt", "rb") as f1:
        bot.send_document(message.chat.id, f1)

# Функция для создания клавиатуры с нужными кнопками
def create_keyboard(buttons_list):
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons_list)
    return keyboard

# Приветственное сообщение /start
@bot.message_handler(commands=['start'])
def start(message):
    global current_options # Для конкретного пользователя устанавливаем его предмет и уровень
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    bot.send_message(message.chat.id,
                     text= f"Привет, {user_name}! Я бот-помощник для решения разных задач!\n"
                            f"Ты можешь прислать условие задачи, а я постараюсь её решить.\n"
                            f"Иногда ответы получаются слишком длинными - в этом случае ты можешь попросить продолжить.",
                     reply_markup=create_keyboard(["/solve_task", '/help']))
    # Создаем пользователя в словаре выбора, с внутренним словарем, где хранятся предмет и уровень
    current_options[message.from_user.id] = {'subject': '', 'level': ''}
    log_current_options_start = current_options[message.from_user.id]
    logging.info(f"log_current_options_start = {log_current_options_start}")
    #execute_query(DB_NAME, f"INSERT INTO users (user_id) "
    #                       f"VALUES ({user_id})")

# Команда /help
@bot.message_handler(commands=['help'])
def support(message):
    bot.send_message(message.from_user.id,
                     text ="Чтобы приступить к решению задачи: нажми /solve_task, а затем напиши условие задачи",
                     reply_markup=create_keyboard(["/solve_task"]))

# Команда /solve_task и регистрация функции get_promt() / choose_subject() для обработки любого следующего сообщения от пользователя
@bot.message_handler(commands=['solve_task'])
def solve_task(message):
    bot.send_message(message.chat.id, "Выбери предмет:", reply_markup = create_keyboard(['математика', 'физика']))
    bot.register_next_step_handler(message, choose_subject)

# Предоставляем выбор кнопок
def choose_subject(message):
    user_id = message.from_user.id
    global current_options
    logging.info(f"choose_subject message ДО выбора = {message.text}")
    # Меняем в словаре выбора значение предмета на основании сообщения пользователя
    current_options[message.from_user.id]['subject'] = message.text
    logging.info(f"choose_subject message ДО выбора = {message.text}")
    logging.info(f" current_options / choose_subject  = {current_options}")

    if current_options[user_id]['subject'] not in ['математика', 'физика']:
        bot.send_message(user_id, text="Ты не выбрал предмет из кнопок")
        solve_task(message)
        return

    bot.send_message(message.chat.id, "Выбери уровень:", reply_markup=create_keyboard(['простой', 'сложный']))
    #logging.info(f"choose_subject [message.from_user.id]['subject'] = {[message.from_user.id]['subject']}")
    bot.register_next_step_handler(message, choose_level)
    # update_row_value(user_id, 'subject', {message.text})
def choose_level(message):
    user_id = message.from_user.id
    global current_options
    logging.info(f"choose_level message ДО выбора = {message.text}")
    # Меняем в словаре выбора значение уровня на основании сообщения пользователя
    current_options[message.from_user.id]['level'] = message.text
    logging.info(f"choose_level = {message.text}")
    logging.info(f" current_options /choose level  = {current_options}")

    if current_options[user_id]['level'] not in ['простой', 'сложный']:
        bot.send_message(user_id, text="Ты не выбрал уровень из кнопок")
        choose_subject(message)
        return
    logging.info(f"choose_level message ПОСЛЕ выбора = {message.text}")
    bot.send_message(message.chat.id, "Задай свой вопрос")
    bot.register_next_step_handler(message, get_promt)

# Фильтр для обработки кнопки "Продолжить решение"
def continue_filter(message):
    button_text = "Продолжить решение"
    return message.text == button_text

# Получение задачи от пользователя или продолжение решения
@bot.message_handler(func=continue_filter)
def get_promt(message):
    global current_options, cur_subject, cur_level
    user_id = message.from_user.id
    logging.info(f"user_id / get_promt = {user_id}")
    if message.content_type != "text":
        bot.send_message(user_id, "Необходимо отправить именно текстовое сообщение")
        bot.register_next_step_handler(message, get_promt)
        return
    # Получаем текст от пользователя
    user_request = message.text
    logging.info(f"user_request / get_promt = {user_request}")
    logging.info(f" ДО execute_query {user_id}, {current_options[user_id]['subject']}, {current_options[user_id]['level']}, {user_request}")
    if len(user_request) > MAX_LETTERS:
        bot.send_message(user_id, "Запрос превышает количество символов\nИсправь запрос")
        bot.register_next_step_handler(message, get_promt)
        return
    logging.info(f"user_id / get_promt = {user_id}")
    logging.info(f"users_history / get_promt = {users_history}")
    #logging.info(f"users_history[user_id] / get_promt = {users_history[user_id]}")
    if user_id not in users_history or users_history[user_id] == {}:
        if user_id not in current_options:
            bot.send_message(user_id, text="Ты не зарегистрировался")
            start(message)
            return
        logging.info(f"current_options[user_id]['subject'] / get_promt = {current_options[user_id]['subject']}")
        if current_options[user_id]['subject'] in ['математика', 'физика']:
            cur_subject = current_options[user_id]['subject'][:-1]+'е'
        if current_options[user_id]['level'] in ['простой', 'сложный']:
            cur_level = current_options[user_id]["level"][:-2] + "ым"
        # Сохраняем промт пользователя и начало ответа GPT в словарь users_history
        users_history[user_id] = {
            'system_content': f"Ты дружелюбный помощник для решения задач по {cur_subject}. Давай ответ {cur_level} языком",
            'user_content': user_request,
            'assistant_content': "Решим задачу по шагам:"
        }
# GPT: Формирование промта и отправка запроса к нейросети
    promt =gpt.make_promt(users_history[user_id])
    resp = gpt.send_request(promt)

# GPT: Проверка ошибок и обработка ответа
    answer = gpt.process_resp(resp)
    logging.info(f" ДО execute_query {user_id}, {cur_subject}, {cur_level}, {user_request}, {answer[1]}")
    execute_query(DB_NAME, f"INSERT INTO users (user_id, subject, level, task, answer) "
                f"VALUES ({user_id}, '{cur_subject}', '{cur_level}', '{user_request}', '{answer[1]}')")
    users_history[user_id]['assistant_content'] += answer[1]

    bot.send_message(user_id, text=users_history[user_id]['assistant_content'],
                 reply_markup=create_keyboard(["Продолжить решение", "Завершить решение"]))

def end_filter(message):
    button_text = "Завершить решение"
    return message.text == button_text

@bot.message_handler(content_types=['text'], func=end_filter)
def end_task(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Текущее решение завершено")
    logging.info(f"users_history = {users_history}  ДО в end_task")
    users_history[user_id] = {}
    logging.info(f"users_history = {users_history} ПОСЛЕ в end_task")
    #start(message)

bot.polling()



'''
currect_subjects = {}
currect_levels = {}
currect_tasks = {}
currect_answers = {}

# Создаёт клавиатуру с указанными кнопками
def menu_keyboard(options):
    buttons = (types.KeyboardButton(text=option) for option in options)
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True,
                                         one_time_keyboard=True)
    keyboard.add(*buttons)
    return keyboard

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    user_name = message.from_user.first_name
    bot.send_message(message.chat.id, f"Привет, {user_name}! Я бот-помощник для решения задач по разным предметам!",
                     reply_markup=menu_keyboard(["/help_with_maths", "/help_with_art"]))
    bot.register_next_step_handler(message, choose_subject)

# Обработчик команды /help_with
@bot.message_handler(commands=["help_with_maths", "help_with_art"])
def choose_subject(message):
    user_id = message.from_user.id # Получаем идентификатор пользователя

        subject = COMMAND_TO_SUBJECT.get(message.text) # Получаем из словаря название предмета
        currect_subjects[user_id] = subject # Запоминаем его

# Предлагаем пользователю выбрать уровень сложности
    bot.send_message(message.chat.id, "Выбери свой уровень знаний:\n"
                                          "beginner - начинающий\n"
                                          "advanced - продвинутый",
                         reply_markup=menu_keyboard(['beginner', 'advanced']))
    bot.register_next_step_handler(message, choose_level) # Регистрируем функцию-обработчик для выбора уровня

# Обработчик для решения задачи
@bot.message_handler(func=command_filter)
def give_answer(message: Message):
    user_id = message.from_user.id # Извлекаем идентификатор пользователя
    user_task = message.text # Извлекаем текст задачи

    subject = currect_subjects.get(user_id) # Получаем предмет, выбранный пользователем на предыдущем этапе
    level = currect_levels.get(user_id) # Получаем уровень сложности, выбранный пользователем на предыдущем этапе

    if not subject: # Если предмет не был указан, просим вернуться к предыдущему шагу
        bot.send_message(message.chat.id, "Пожалуйста, выбери предмет, нажав на кнопку",
                         reply_markup=menu_keyboard(["/help_with_maths", "/help_with_art"]))
        return

    if not level: # Если уровень не был указан, просим вернуться к предыдущему шагу
        bot.send_message(message.chat.id, "Пожалуйста, выбери уровень сложности",
                         reply_markup=menu_keyboard(['beginner', 'advanced']))
        return

        # Выполняем проверку на размер задачи
    if count_tokens(message.text) > MAX_TASK_TOKENS:
        currect_tasks[user_id] = ""
        currect_answers[user_id] = ""

        bot.send_message(message.chat.id, "Текст задачи слишком длинный. Пожалуйста, попробуй его укоротить.")
        logging.info(f"TELEGRAM BOT: Input: {message.text}\nOutput: Текст задачи слишком длинный")
        return

      # Если всё хорошо, бот должен дать ответ
    bot.send_message(message.chat.id, "Решаю...")
    currect_tasks[user_id] = user_task # Запоминаем задачу пользователя

    system_promt = PROMPTS_TEMPLATES[subject][level]['system'] # Получаем нужный системный промт по предмету и уровню
    answer = ask_gpt_helper(message.text, system_promt) # Получаем ответ от GPT

        # ... обработка ответа аналогично первому проекту
    '''