from telebot import TeleBot
from telebot.types import Message, ReplyKeyboardMarkup
from content import users_info, users_state, USERS_STATES_TEXT, CONTENT, Roles, Modes
from gpt import create_system_prompt, count_tokens_in_text, get_gpt_answer
from config import TG_TOKEN, MAX_TOKENS_IN_SESSION, MAX_SESSIONS
from db import create_db, create_table, insert_row, count_tokens_for_user_in_session, \
    get_all_unique_messages_in_session, get_last_session, is_max_amount_of_users, is_user_in_db

bot = TeleBot(TG_TOKEN)


def check_user_info_created(message: Message):
    return users_info.get(message.chat.id)


def get_text_state(cur_state_num):
    return USERS_STATES_TEXT[cur_state_num]


def create_keyboard(text_buttons):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
    markup.add(*text_buttons)
    return markup


@bot.message_handler(commands=['start'])
def start_handler(message: Message):
    user_name = message.from_user.first_name
    bot.send_message(message.chat.id, f'Привет, {user_name}! Я - классный бот, который отвечает на вопросы!\n'
                                            'Выбери жанр ответа, эксперта и его настроение\n'
                                            "После получения ответа ты можешь уточнить детали\n"
                                            f"Выбери кнопку /new_story, чтобы начать.",
                                        reply_markup=create_keyboard(["/new_story"]))

@bot.message_handler(commands=['new_story'])
def new_story_handler(message: Message):
    if is_max_amount_of_users() and not is_user_in_db(message.chat.id):
        bot.send_message(message.chat.id, 'Количество юзеров превышено!')
        return

    users_info[message.chat.id] = {
        'session_id': get_last_session(message.chat.id) + 1
    }
    user_state_num = users_state[message.chat.id] = 0
    user_state = get_text_state(user_state_num)

    markup = create_keyboard(CONTENT[user_state]['buttons_text'])

    bot.send_message(message.chat.id,
                     'Ты начал новую историю.')
    bot.send_message(message.chat.id,
                     CONTENT[user_state]['text'],
                     reply_markup=markup)
    bot.register_next_step_handler(message, process_choice)


def process_choice(message: Message):
    cur_user_state_num = users_state[message.chat.id]
    cur_user_state_text = get_text_state(cur_user_state_num)
    cur_content = CONTENT[cur_user_state_text]
    buttons_text = cur_content['buttons_text']

    if message.text not in buttons_text:
        bot.send_message(message.chat.id,
                         'Нажимай на кнопочки!',
                         reply_markup=create_keyboard(buttons_text))
        bot.register_next_step_handler(message, process_choice)
        return

    users_info[message.chat.id][cur_user_state_text] = message.text

    users_state[message.chat.id] += 1
    cur_user_state_num += 1

    if cur_user_state_num >= len(USERS_STATES_TEXT):
        bot.send_message(message.chat.id, 'Круто, пиши запрос нейросети,\n '
                                          'Или можешь ввести информацию голосом')
        return

    cur_user_state_text = get_text_state(cur_user_state_num)
    cur_content = CONTENT[cur_user_state_text]

    message_text = cur_content['text']
    buttons_text = cur_content['buttons_text']

    bot.send_message(message.chat.id, message_text,
                     reply_markup=create_keyboard(buttons_text))
    bot.register_next_step_handler(message, process_choice)


@bot.message_handler(commands=['additional'], func=check_user_info_created)
def additional_handler(message: Message):
    bot.send_message(message.chat.id, 'Вводи доп инфу!')
    bot.register_next_step_handler(message, process_additional)


def process_additional(message: Message):
    users_info[message.chat.id]['additional'] = message.text
    bot.send_message(message.chat.id, 'Принято!')


@bot.message_handler(commands=['end'])
def end_handler(message: Message):
    session_id = users_info[message.chat.id]['session_id']
    gpt_answer = ask_gpt(message.chat.id, session_id, Modes.END)
    users_info[message.chat.id] = {}
    bot.send_message(message.chat.id, gpt_answer)


@bot.message_handler(content_types=['text'], func=check_user_info_created)
def ask_gpt_handler(message: Message):
    session_id = users_info[message.chat.id]['session_id']

    if session_id > MAX_SESSIONS:
        bot.send_message(message.chat.id, 'Вы израсходовали все свои сессии!')
        return

    system_prompt = create_system_prompt(message.chat.id)
    system_tokens = count_tokens_in_text(system_prompt)

    insert_row((message.chat.id, Roles.SYSTEM, system_prompt, system_tokens, session_id))

    user_tokens = count_tokens_in_text(message.text)

    insert_row((message.chat.id, Roles.USER, message.text, user_tokens, session_id))

    tokens = count_tokens_for_user_in_session(message.chat.id, session_id)
    if tokens >= MAX_TOKENS_IN_SESSION:
        bot.send_message(message.chat.id, 'ТУ МАЧ, превышено количество токенов в сессии')
        end_handler(message)
        return

    gpt_answer = ask_gpt(message.chat.id, session_id, Modes.CONTINUE)

    bot.send_message(message.chat.id, gpt_answer)


def ask_gpt(user_id, session_id, mode):
    user_history = get_all_unique_messages_in_session(user_id, session_id)

    gpt_answer, assistant_tokens = get_gpt_answer(user_history, mode)

    insert_row((user_id, Roles.ASSISTANT, gpt_answer, assistant_tokens, session_id))

    return gpt_answer


@bot.message_handler(content_types=['text'])
@bot.message_handler(commands=['help'])
def help_handler(message: Message):
    bot.send_message(message.chat.id, 'Введи /new_story чтобы начать')


create_db()
create_table()

bot.polling()
