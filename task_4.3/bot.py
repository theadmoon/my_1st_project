import math
from database import create_table, insert_row, count_all_blocks
from speechkit import speech_to_text
import logging
import telebot
from telebot import TeleBot
from config import MAX_USER_STT_BLOCKS, MAX_SESSIONS, MAX_USER_TOKENS, TOKEN, MAX_USER_TTS_SYMBOLS, MAX_TTS_SYMBOLS
import telebot
from telebot import types
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup

bot = TeleBot(TOKEN)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="log_file.txt",
    filemode="w",
)
logging.basicConfig(level=logging.INFO)

create_table()

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

    bot.send_message(message.chat.id,
                     text= f"Привет, {user_name}! Я бот, который распознает аудио и возвращает сообщение в виде текста\n"
                           f"Выбери кнопку /stt, чтобы начать.",
                    reply_markup=create_keyboard(["/stt"]))

#    log_current_options_start = current_options[message.from_user.id]
#    logging.info(f"log_current_options_start = {log_current_options_start}")

# Обрабатываем команду /stt
@bot.message_handler(commands=['stt'])
def stt_handler(message):
    user_id = message.from_user.id
    bot.send_message(user_id, 'Отправь голосовое сообщение, чтобы я его распознал!')
    bot.register_next_step_handler(message, stt)


# Переводим голосовое сообщение в текст после команды stt
def stt(message):
    user_id = message.from_user.id

    # Проверка, что сообщение действительно голосовое
    if not message.voice:
        return

    # Считаем аудиоблоки и проверяем сумму потраченных аудиоблоков
    stt_blocks = is_stt_block_limit(message, message.voice.duration)
    if not stt_blocks:
        return

    file_id = message.voice.file_id  # получаем id голосового сообщения
    print("file_id =", file_id)
    file_info = bot.get_file(file_id)  # получаем информацию о голосовом сообщении
    print("file_info =", file_info)
    file = bot.download_file(file_info.file_path)  # скачиваем голосовое сообщение

    # Получаем статус и содержимое ответа от SpeechKit
    status, text = speech_to_text(file)  # преобразовываем голосовое сообщение в текст
    print("status, text =", status, text)
    # Если статус True - отправляем текст сообщения и сохраняем в БД, иначе - сообщение об ошибке
    if status:
        # Записываем сообщение и кол-во аудиоблоков в БД
        insert_row(user_id, text, 'stt_blocks', stt_blocks)
        if not text:
            text = "Плохое качество аудио, попробуйте записать звук еще раз"
        bot.send_message(user_id, text, reply_to_message_id=message.id)

        bot.register_next_step_handler(message, stt)
    else:
        bot.send_message(user_id, text)

def is_stt_block_limit(message, duration):
    user_id = message.from_user.id

    # Переводим секунды в аудиоблоки
    audio_blocks = math.ceil(duration / 15) # округляем в большую сторону
    # Функция из БД для подсчёта всех потраченных пользователем аудиоблоков
    all_blocks = count_all_blocks(user_id) + audio_blocks

    # Проверяем, что аудио длится меньше 30 секунд
    if duration >= 30:
        msg = "SpeechKit STT работает с голосовыми сообщениями меньше 30 секунд"
        bot.send_message(user_id, msg)
        return None

    # Сравниваем all_blocks с количеством доступных пользователю аудиоблоков
    if all_blocks >= MAX_USER_STT_BLOCKS:
        msg = f"Превышен общий лимит SpeechKit STT {MAX_USER_STT_BLOCKS}. Использовано {all_blocks} блоков. Доступно: {MAX_USER_STT_BLOCKS - all_blocks}"
        bot.send_message(user_id, msg)
        return None

    return audio_blocks

bot.polling()
...