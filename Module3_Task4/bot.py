import json
import os.path
import logging
import sqlite3
from datetime import datetime
import telebot
from telebot import types
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup
from config import TOKEN,  MAX_USERS, MAX_TOKENS, END_STORY
from gpt import ask_gpt, create_promt, count_tokens_in_dialogue, GPT
from database import (
    get_dialogue_for_user,
    add_record_to_table,
    get_value_from_table,
    #    count_all_tokens_from_db,
    execute_selection_query,
    #    get_users_amount,
    create_db,
    create_table,
    DB_NAME,
    DB_TABLE_PROMPTS_NAME,
    is_value_in_table,
    get_users_amount, execute_query,
    #    execute_query,
    #    update_row_value
)
# Создаем бота
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
user_data = {}
# Словарь для хранения текущего выбора пользователем предмета и уровня
current_options = {}
create_db(DB_NAME)
create_table(DB_TABLE_PROMPTS_NAME)
genres = ['Horror', 'Comedy', 'Fantastic']
heroes = ['Ведьма', 'Скунс', 'Робот', 'Дракон']
settings = ['Город', 'Природа', 'Магия']

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
    user_name = message.from_user.first_name
    user_id = message.from_user.id

    user_data[user_id]= {
        'session_id': 0,
        'genre': None,
        'hero': None,
        'setting': None,
        'additional_info': None,
        'state': 'регистрация',
        'test_mode': False
    }
    bot.send_message(message.chat.id,
                     text= f"Привет, {user_name}! Я бот, который создает истории с помощью нейросети!\n"
                           f"Мы будем писать историю поочередно. Я начну, а ты продолжишь.\n"
                        f"Выбери кнопку /new_story, чтобы начать новую историю."
                        f"А когда закончишь, нажми кнопку /end",
                    reply_markup=create_keyboard(["/new_story", '/help']))
    # Создаем пользователя в словаре выбора, с внутренним словарем, где хранятся предмет и уровень
    #current_options[message.from_user.id] = {'genre': '', 'hero': '', 'setting': '', 'user_answer': ''}
#    log_current_options_start = current_options[message.from_user.id]
#    logging.info(f"log_current_options_start = {log_current_options_start}")
    execute_query(DB_NAME, f"INSERT INTO {DB_TABLE_PROMPTS_NAME} (user_id) "
                           f"VALUES ({user_id})")
'''
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
'''
# Команда /help
@bot.message_handler(commands=['help'])
def support(message):
    bot.send_message(message.from_user.id,
                     text ="Чтобы приступить к написанию истории: нажми /new_story, а затем выбери жанр, героя и сеттинг. Дополняй историю после ответа нейросети",
                     reply_markup=create_keyboard(["/new_story"]))

# Обработчик команды /begin
@bot.message_handler(commands=['begin'])
def begin_story(message):
    user_id = message.from_user.id
    # Проверяем, что пользователь прошел регистрацию
    if not user_data.get(user_id):
        bot.send_message(message.chat.id, "Введи /start, тебя еще нет в регистрации на игру")
        return
    if user_data[user_id]['state'] == "регистрация":
        bot.send_message(message.chat.id, "Чтобы начать писать историю, нужно пройти небольшой опрос.\n"
                                                "Напиши /new_story и ответь на все вопросы, чтобы начать сочинять.",
                        reply_markup=create_keyboard(['/new_story']))
        return
    user_data[user_id]["state"] = "в истории"
    # Запрашиваем ответ нейросети
    get_story(message)

@bot.message_handler(commands=['all_tokens'])
def send_tokens(message):
    try:
        all_tokens = count_all_tokens_from_db()
        bot.send_message(
            message.chat.id,
            f"За все время использования бота\n"
                f"израсходовано токенов - {all_tokens}",
            reply_markup=create_keyboard(['/new_story'])
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"Произошла ошибка при получении информации о токенах: {e}"
        )
        logging.debug(f"Произошла ошибка при получении информации о токенах: {e}")

@bot.message_handler(commands=["end"])
def end_the_story(message):
    user_id = message.from_user.id
    if not is_value_in_table(DB_TABLE_PROMPTS_NAME, "user_id", user_id):
        bot.send_message(message.chat.id, "Ты еще не начал историю. Напиши /begin, чтобы начать",
                        reply_markup=create_keyboard(['/begin']))
        return
    story_handler(message,'end')
    bot.send_message(message.chat.id, "Спасибо, что писал со мной историю!",
                     reply_markup=create_keyboard(['/new_story', '/whole_story', '/all_tokens', '/debug']
    ))

@bot.message_handler(commands=['whole_story'])
def get_the_whole_story(message):
    user_id = message.from_user.id

    session_id = None
    if is_value_in_table(DB_TABLE_PROMPTS_NAME, 'user_id', user_id):
        row: sqlite3.Row = get_value_from_table('session_id', user_id)
        session_id = row['session_id']

    if not session_id:
        bot.send_message(message.chat.id, "Ты еще не начал историю."
                                               "\nНапиши /begin, чтобы начать.",
                         reply_markup=create_keyboard(['/begin']))
        return
    collection: sqlite3.Row = get_value_from_table(user_id, session_id)
    whole_story = ''
    for row in collection:
        whole_story += row['content'] + "\n"
    sql_query = f'SELECT content FROM {DB_TABLE_PROMPTS_NAME} WHERE user_id = ? AND role = ? ORDER BY DATE'
    data = (user_id, "system")
    promt = execute_selection_query(sql_query, data)
    whole_story = whole_story.replace(promt[0]['content'], '')

    bot.send_message(message.chat.id, "Вот история, которая у нас пока получилась:")
    bot.send_messge(message.chat.id, whole_story, reply_markup =create_keyboard(
        [
            '/new_story',
            '/all_tokens',
            '/debug'
        ]
    ))
# Обработчик команды /new_story
@bot.message_handler(commands=['new_story'])
def registration(message):
    # Меняет статус пользователя на "в истории"
    # ЗАписывает в бд и отправляет первый запрос о жанре
    users_amount = get_users_amount(DB_TABLE_PROMPTS_NAME)
    if users_amount >= MAX_USERS:
        bot.send_message(message.chat.id, "Лимит пользователей для регистрации превышен")
        return

    bot.send_message(message.chat.id, "Для начала выбери жанр своей истории:\n",
                     reply_markup=create_keyboard(genres))
    bot.register_next_step_handler(message, handle_genre)

def handle_genre(message):
    # Записывает ответ на вопрос о жанре в БД и отправляет следующий вопрос о персонаже
    user_id = message.from_user.id
    # считывает ответ на предыдущий вопрос
    genre = message.text
    # Если пользователь отвечает что-то не то, то отправляет ему вопрос ещё раз
    if genre not in genres:
        bot.send_message(message.chat.id, "Выбери один из предложенных на клавиатуре жанров:",
                         reply_markup=create_keyboard(genres))
        bot.register_next_step_handler(message, handle_genre)
        return
    # Обновляет данные пользователя
    user_data[user_id]['genre'] = genre
    user_data[user_id]['state'] = "в истории"
    # Отправляет следующий вопрос
    bot.send_message(message.chat.id, "Выбери главного героя:",
                     reply_markup=create_keyboard(heroes))
    bot.register_next_step_handler(message, handle_hero)

def handle_hero(message):
    # Записывает ответ на вопрос о герое в БД и отправляет следующий вопрос о сеттинге
    user_id = message.from_user.id
    # считывает ответ на предыдущий вопрос
    hero = message.text
    # Если пользователь отвечает что-то не то, то отправляет ему вопрос ещё раз
    if hero not in heroes:
        bot.send_message(message.chat.id, "Выбери один из предложенных на клавиатуре героев:",
                         reply_markup=create_keyboard(heroes))
        bot.register_next_step_handler(message, handle_hero)
        return
    # Обновляет данные пользователя
    user_data[user_id]['hero'] = hero
    bot.send_message(message.chat.id, "Выбери сеттинг:\n"
                                            f"Город: История происходит в современном городе с высокими небоскребами, оживленными улицами и разнообразными районами.\n"
                                            f"Природа: История происходит в лесу, где растут большие деревья, и много разных животных.\n"
                                            f"Магия: История развивается в мире с волшебством, магией и фантастическими созданиями.",
                     reply_markup=create_keyboard(['Город', 'Природа', 'Магия']))
    '''
    settings_string = "\n.join([f"{name}: {description}" for name, description in settings.items()])
    # Отправляет следующий вопрос
    bot.send_message(message.chat.id, "Выбери сеттинг:\n + settings_string",
                     reply_markup=create_keyboard(settings.keys())
    '''
    bot.register_next_step_handler(message, handle_setting)

def handle_setting(message):
    # Записывает ответ на вопрос о сеттинге в БД и отрпавляет следующий вопрос о доп.инфо
    user_id = message.from_user.id
    # Считывает ответ на предыдущий вопрос
    user_setting = message.text
    # Если пользователь отвечает что-то не то, то отправляет ему вопрос ещё раз
    if user_setting not in settings:
        bot.send_message(message.chat.id, "Выбери один из предложенных на клавиатуре сеттингов:",
                         reply_markup=create_keyboard(settings))
        bot.register_next_step_handler(message, handle_setting)
        return
    # Обновляет данные пользователя в БД
    user_data[user_id]['setting'] = user_setting
    user_data[user_id]['state'] = 'регистрация пройдена'

    # Отправляет следующий вопрос
    logging.info(f"choose_setting message ПОСЛЕ выбора = {message.text}")
    bot.send_message(message.chat.id, "Если ты хочешь, чтобы мы учли еще какую-то информацию, напиши ее сейчас.\n"
                                            f"Или ты можешь сразу переходить к истории, для этого нажми /begin",
                     reply_markup=create_keyboard(["/begin"]))
    bot.register_next_step_handler(message, handle_add_info)

def handle_add_info(message):
    # Записывает ответ на вопрос о доп.инфор в БД
    user_id = message.from_user.id
    # Считывает ответ на предыдущий вопрос
    additional_info = message.text

    if additional_info == "/begin":
        begin_story(message)
    else:
        # Обновляет данные пользователя в БД
        user_data[user_id]['additional_info'] = additional_info
        # Отправляет следующее сообщение и запрос
        bot.send_message(user_id, text="Мы учли полученную информацию, спасибо! "
                                        "Теперь нажми /begin, чтобы начать писать историю.",
                         reply_markup=create_keyboard(['/begin']))
'''
@bot.message_handler(content_types=['text'])
def answer_handler(message: types.Message):
    user_id: int = message.from_user.id
    user_answer: str = message.text

    if user_answer in HELP_COMMANDS:
        solve_task(message)
        return

    tokens: int = count_tokens(user_answer)

    if is_tokens_limit(message, tokens, bot):
        return

    row: sqlite3.Row = get_value_from_table('session_id', user_id)

    add_record_to_table(
        user_id,
        'user',
        user_answer,
        datetime.now(),
        tokens,
        row['session_id']
    )
    bot.send_message(message.chat.id, "Генерирую ответ...")

    collection: sqlite3.Row = get_dialogue_for_user(user_id, row['session_id'])
    gpt_text: str = ask_gpt(gpt_text)
    tokens: int = count_tokens(gpt_text)

    if is_tokens_limit(message, tokens, bot):
        return
    add_record_to_table(
        user_id,
        'assistant',
        gpt_text,
        datetime.now(),
        tokens,
        row['session_id']
    )

    bot.send_message(message.chat.id, gpt_text, reply_markup=create_keyboard(HELP_COMMANDS))
'''
@bot.message_handler(content_types=['text'])
def story_handler(message: types.Message, mode='continue'):
    user_id: int = message.from_user.id
    user_answer: str = message.text

    if mode == 'end':
        user_answer = END_STORY

    row: sqlite3.Row = get_value_from_table('session_id', user_id)
    collection: sqlite3.Row = get_dialogue_for_user(user_id, row['session_id'])
    collection.append({'role': 'user', 'content': user_answer})

    tokens: int = count_tokens_in_dialogue(collection)
#    if is_tokens_limit(message, tokens, bot):
#        return

    add_record_to_table(
        user_id,
        'user',
        user_answer,
        datetime.now(),
        tokens,
        row['session_id']
    )
#    if is_tokens_limit(message, tokens, bot):
#        return

    gpt_text, result_for_test = ask_gpt(collection, mode)

    collection: sqlite3.Row = get_dialogue_for_user(user_id, row['session_id'])
    collection.append({'role': 'assistant', 'content': gpt_text})
    tokens: int = count_tokens_in_dialogue(collection)

    add_record_to_table(
        user_id,
        'assistant',
        gpt_text,
        datetime.now(),
        tokens,
        row['session_id']
    )

    if not user_data[user_id]['test_mode']:
        bot.send_message(message.chat.id, gpt_text, reply_markup=create_keyboard(['/end']))
    else:
        bot.send_message(message.chat.id, result_for_test, reply_markup=create_keyboard('/end'))

# ОБработчик для генерирования вопроса
@bot.message_handler(content_types=['text'])
def get_story(message: types.Message):
    user_id: int =message.from_user.id

#    if is_sessions_limit(message, bot):
#        return
    session_id = 1

    if is_value_in_table(DB_TABLE_PROMPTS_NAME, 'user_id', user_id):
        row: sqlite3.Row = get_value_from_table('session_id', user_id)
        session_id = row['session_id'] + 1

    user_story = create_promt(user_data, message.from_user.id)

    collection: sqlite3.Row = get_dialogue_for_user(user_id, session_id)
    collection.append({'role': 'system', 'content': user_story})
    tokens: int = count_tokens_in_dialogue(collection)

    bot.send_message(message.chat.id, "Генерирую...")

    add_record_to_table(
        user_id,
        'system',
        user_story,
        datetime.now(),
        tokens,
        session_id
    )
    collection: sqlite3.Row = get_dialogue_for_user(user_id, session_id)
    gpt_text, result_for_text = ask_gpt(collection)
    collection.append({'role': 'assistant', 'content': gpt_text})

    tokens: int = count_tokens_in_dialogue(collection)
#    if is_tokens_limit(message, tokens, bot):
#        return
    add_record_to_table(
        user_id,
        'system',
        user_story,
        datetime.now(),
        tokens,
        session_id
    )
    add_record_to_table(
        user_id,
        'assistant',
        gpt_text,
        datetime.now(),
        tokens,
        row['session_id']
    )



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