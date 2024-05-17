���� - ��� �� python, ������� ������ ������: telebot.apihelper.ApiTelegramException: A request to the Telegram API was unsuccessful. Error code: 400. Description: Bad Request: message text is empty
����� �������� ��������� ������ ��������� � ������� ���, ����� �������� ���� ������.
�������� ��� ������ ����


import json
import logging
import telebot
from telebot import ApiTelegramException
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup
from config import TOKEN, MAX_TOKENS
from gpt import GPT

gpt = GPT()

bot = TeleBot(TOKEN)
MAX_LETTERS = MAX_TOKENS


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


def create_keyboard(buttons_list):
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons_list)
    return keyboard


@bot.message_handler(commands=['start'])
def start(message):
    user_name = message.from_user.first_name
    bot.send_message(message.chat.id,
                     text=f"������, {user_name}! � ���-��������.",
                     reply_markup=create_keyboard(["/solve_task", '/help']))


@bot.message_handler(commands=['debug'])
def send_logs(message):
    with open("log_file.txt", "rb") as f1:
        bot.send_document(message.chat.id, f1)


@bot.message_handler(commands=['solve_task'])
def solve_task(message):
    bot.send_message(message.chat.id, "����� �����, ��� �������� �������� ������� �����:")
    bot.register_next_step_handler(message, get_promt)


def continue_filter(message):
    button_text = '���������� �������'
    return message.text == button_text


# ��������� ������ �� ������������ ��� ����������� �������
@bot.message_handler(func=continue_filter)
def get_promt(message):
    user_id = str(message.from_user.id)  # �����!

    #   �������� �� ��� ��������� (�����, ��������, ����� � ��). ���� ��� �� ����� - ��������� �� ������ ������������,

    if not message.text:
        bot.send_message(user_id, "���������� ��������� ������ ��������� ���������")
        # C�������� ��������� ������������ �������� � ��� �� ������� - get_promt()
        bot.register_next_step_handler(message, get_promt)
        return

    # �������� ����� ��������� �� ������������
    user_request = message.text

    # if len(user_request) >= MAX_TOKENS:
    #     bot.send_message(user_id, "������ ��������� ���������� ��������\n������� ������")
    #     bot.register_next_step_handler(message, get_promt)
    #     return

    # �������� ������ ������������ �� ���������� �������. ���� ���������� �������� ������ - ��������� �� ������ ������������
    if gpt.count_tokens(user_request) >= gpt.MAX_TOKENS:
        bot.send_message(user_id, "������ ��������� ���������� ��������\n������� ������")
        bot.register_next_step_handler(message, get_promt)
        return

    # ��������: ���� � ������������ ��� ������� ������, ����� �� ����� ������
    if user_id not in users_history or users_history[user_id] == {}:
        if user_request == "���������� �������":
            bot.send_message(message.chat.id, "�������, �� ��� �� ������ ������.")
            bot.register_next_step_handler(message, get_promt)
            return
        # ��������� ����� ������������ � ������ ������ GPT � �������� users_history
        users_history[user_id] = {
            'system_content': (
                "�� ���."
                "����� ����������� ���������� �� 1 �� 10."),
            'user_content': user_request,
            'assistant_content': "����� �����: "
        }
        save_to_json()

    # ���� ��� ������� �� GPT ����� ����� �����, ������ �������� ���)
    # answer = "����� ����� ����� �������� �������, � ���� ��� ��� :)"
    prompt = gpt.make_promt(users_history[user_id])
    resp = gpt.send_request(prompt)
    answer = resp.json()['choices'][0]['message']['content']

    # ���������� ���� ����� �� GPT � ����������� ������ GPT
    users_history[user_id]["assistant_content"] += answer
    save_to_json()

    keyboard = create_keyboard(["���������� �������", "��������� �������"])
    bot.send_message(message.chat.id, answer, reply_markup=keyboard)


# ������ ��� ��������� �������� "��������� �������"
@bot.message_handler(commands=['end'])
@bot.message_handler(content_types=['text'], func=lambda message: message.text.lower() == "��������� �������")
def end_task(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "������� ������� ���������")
    users_history[user_id] = {}
    solve_task(message)


bot.polling()
