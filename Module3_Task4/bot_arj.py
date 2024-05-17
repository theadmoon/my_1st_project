import json
import logging
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup
from config import TOKEN, MAX_TOKENS
from gpt import GPT
from database_arj import create_db, create_table, DB_NAME, execute_query, update_row_value, DB_TABLE_USERS_NAME

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
create_table(DB_TABLE_USERS_NAME)

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
                     text= f"Привет, {user_name}! Я бот, который создает истории с помощью нейросети!\n"
                           f"Мы будем писать историю поочередно. Я начну, а ты продолжишь.\n"
                        f"Выбери кнопку /new_story, чтобы начать новую историю."
                        f"А когда закончишь, нажми кнопку /end",
                    reply_markup=create_keyboard(["/new_story", '/help']))
    # Создаем пользователя в словаре выбора, с внутренним словарем, где хранятся предмет и уровень
    current_options[message.from_user.id] = {'genre': '', 'hero': '', 'setting': '', 'user_answer': ''}
    log_current_options_start = current_options[message.from_user.id]
    logging.info(f"log_current_options_start = {log_current_options_start}")
    #execute_query(DB_NAME, f"INSERT INTO users (user_id) "
    #                       f"VALUES ({user_id})")

# Команда /help
@bot.message_handler(commands=['help'])
def support(message):
    bot.send_message(message.from_user.id,
                     text ="Чтобы приступить к написанию истории: нажми /new_story, а затем выбери жанр, героя и сеттинг. Дополняй историю после ответа нейросети",
                     reply_markup=create_keyboard(["/new_story"]))

# Команда /solve_task и регистрация функции get_promt() / choose_subject() для обработки любого следующего сообщения от пользователя
@bot.message_handler(commands=['new_story'])
def new_story(message):
    bot.send_message(message.chat.id, "Для начала выбери жанр своей истории:", reply_markup = create_keyboard(['Horror', 'Comedy', 'Fantastic']))
    bot.register_next_step_handler(message, choose_genre)

# Предоставляем выбор кнопок
def choose_genre(message):
    user_id = message.from_user.id
    global current_options
    logging.info(f"choose_subject message ДО выбора = {message.text}")
    # Меняем в словаре выбора значение предмета на основании сообщения пользователя
    current_options[message.from_user.id]['genre'] = message.text
    logging.info(f"choose_genre message ДО выбора = {message.text}")
    logging.info(f" current_options / choose_genre  = {current_options}")

    if current_options[user_id]['genre'] not in ['Horror', 'Comedy', 'Fantastic']:
        bot.send_message(user_id, text="Ты не выбрал жанр из кнопок")
        new_story(message)
        return

    bot.send_message(message.chat.id, "Выбери главного героя:", reply_markup=create_keyboard(['Ведьма', 'Скунс', 'Робот', 'Дракон']))
    #logging.info(f"choose_subject [message.from_user.id]['subject'] = {[message.from_user.id]['subject']}")
    bot.register_next_step_handler(message, choose_hero)
    # update_row_value(user_id, 'subject', {message.text})
def choose_hero(message):
    user_id = message.from_user.id
    global current_options
    logging.info(f"choose_hero message ДО выбора = {message.text}")
    # Меняем в словаре выбора значение уровня на основании сообщения пользователя
    current_options[message.from_user.id]['hero'] = message.text
    logging.info(f"choose_hero = {message.text}")
    logging.info(f" current_options /choose hero  = {current_options}")

    if current_options[user_id]['hero'] not in ['Ведьма', 'Скунс', 'Робот', 'Дракон']:
        bot.send_message(user_id, text="Ты не выбрал героя из кнопок")
        choose_genre(message)
        return
    logging.info(f"choose_hero message ПОСЛЕ выбора = {message.text}")
    bot.send_message(message.chat.id, "Выбери сеттинг:\n"
                                            f"Город: История происходит в современном городе с высокими небоскребами, оживленными улицами и разнообразными районами.\n"
                                            f"Природа: История происходит в лесу, где растут большие деревья, и много разных животных.\n"
                                            f"Магия: История развивается в мире с волшебством, магией и фантастическими созданиями.",
                     reply_markup=create_keyboard(['Город', 'Природа', 'Магия']))
    bot.register_next_step_handler(message, choose_setting)

def choose_setting(message):
    user_id = message.from_user.id
    global current_options
    logging.info(f"choose_setting message ДО выбора = {message.text}")
    # Меняем в словаре выбора значение уровня на основании сообщения пользователя
    current_options[message.from_user.id]['setting'] = message.text
    logging.info(f"choose_setting = {message.text}")
    logging.info(f" current_options /choose setting  = {current_options}")

    if current_options[user_id]['setting'] not in ['Город', 'Природа', 'Магия']:
        bot.send_message(user_id, text="Ты не выбрал сеттинг из кнопок")
        choose_hero(message)
        return
    logging.info(f"choose_setting message ПОСЛЕ выбора = {message.text}")
    bot.send_message(message.chat.id, "Если ты хочешь, чтобы мы учли еще какую-то информацию, напиши ее сейчас.\n"
                                            f"Или ты можешь сразу переходить к истории, для этого нажми /begin",
                     reply_markup=create_keyboard(["/begin"]))
    bot.register_next_step_handler(message, text_or_begin)
    logging.info(f"choose_setting message ПОСЛЕ выбора = {message.text}")
def text_or_begin(message):
    user_id = message.from_user.id
    global current_options
    logging.info(f"text_or_begin = {message.text}")

    if message.text == "/begin":
        bot.send_message(user_id, text="Генерирую...",
                         reply_markup=create_keyboard(['/continue']))
    elif message.text:
        bot.send_message(user_id, text="Мы учли полученную информацию, спасибо! "
                                        "Теперь нажми /begin, чтобы начать писать историю",
                         reply_markup=create_keyboard(['/begin']))

        logging.info(f"choose_setting message ДО выбора = {message.text}")
        # Меняем в словаре значение истории на основании сообщения пользователя
        current_options[message.from_user.id]['user_answer'] = message.text
    logging.info(f" current_options /text_or_begin  = {current_options}")
    bot.register_next_step_handler(message, get_promt)

def check_begin(message):
    user_id = message.from_user.id
    logging.info(f"check_begin = {message.text}")
    if message.text != "/begin" or message.text != "/continue":
        bot.send_message(user_id, text="Для продолжения нужно нажать кнопку /begin")
        text_or_begin(message)
        return
    bot.register_next_step_handler(message, get_promt)
    logging.info(f"check_begin после хендлера = {message.text}")
def continue_filter(message):
    button_text = "Продолжить историю"
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
    logging.info(f" ДО execute_query {user_id}, {current_options[user_id]['genre']}, {current_options[user_id]['hero']}, {current_options[user_id]['setting']}, {user_request}")
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
        logging.info(f"current_options[user_id]['genre'] / get_promt = {current_options[user_id]['genre']}")
        if current_options[user_id]['gengre'] in ['Horror', 'Comedy', 'Fantastic']:
            cur_subject = current_options[user_id]['genre'][:-1]+'е'
        if current_options[user_id]['hero'] in ['Ведьма', 'Скунс', 'Робот', 'Дракон']:
            cur_level = current_options[user_id]["hero"][:-2] + "ым"
        if current_options[user_id]['setting'] in ['Город', 'Природа', 'Магия']:
            cur_subject = current_options[user_id]['setting'][:-1]+'е'

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