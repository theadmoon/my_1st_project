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

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="log_file.txt",
    filemode="w",
)


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


# Функция для создания клавиатуры с нужными кнопочками
def create_keyboard(buttons_list):
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons_list)
    return keyboard

# Приветственное сообщение /start
@bot.message_handler(commands=['start'])
def start(message):
    user_name = message.from_user.first_name
    bot.send_message(message.chat.id,
                     text=f"Привет, {user_name}! Я бот-помощник для обзора аллергенной обстановки!\n"
                          f"Ты можешь прислать название города, а я постараюсь сообщить какие там сейчас риски.\n"
                          "Иногда ответы получаются слишком длинными - в этом случае ты можешь попросить продолжить.",
                     reply_markup=create_keyboard(["/solve_task", '/help']))

# Создание отчета логов /debug
@bot.message_handler(commands=['debug'])
def send_logs(message):
    with open("log_file.txt", "rb") as f1:
        bot.send_document(message.chat.id, f1)

# Команда /help
@bot.message_handler(commands=['help'])
def support(message):
    bot.send_message(message.from_user.id,
                     text="Чтобы получить обзор аллергенной обстановки: нажми /solve_task, а затем укажи город",
                     reply_markup=create_keyboard(["/solve_task"]))


# Команда /solve_task и регистрация функции get_promt() для обработки любого следующего сообщения от пользователя
@bot.message_handler(commands=['solve_task'])
def solve_task(message):
    bot.send_message(message.chat.id, "Укажи город, для которого уточняем аллерго риски:")
    bot.register_next_step_handler(message, get_promt)

# Фильтр для обработки кнопочки "Продолжить решение"
def continue_filter(message):
    button_text = 'Продолжить решение'
    return message.text == button_text

'''
# Токен вашего бота
# token = 'TOKEN_YOUR_BOT'

try:
    # Создаем экземпляр TeleBot
    bot = telebot.TeleBot(token)
except ApiTelegramException as e:
    if e.error_code == 400 and 'message text is empty' in e.description:
        print('Ошибка: пустое сообщение')
        # Здесь необходимо решить проблему с пустыми сообщениями, например, проверив токен бота и исправив код генерации сообшений.
        # Для тестов можно выводить статус-сообщение для администратора бота
        bot.send_message(chat_id='ID_ADMIN', text='Бот рабочий, но на данный момент не может отправлять пустые сообщения. Проверяем токен и исправляем код!')
    else:
        print('Статус ошибки:', e)

 Before diving into the code, it's important to note that the main reason for empty messages might be due to an incorrect or expired token. Let's start by checking the token and then we'll proceed with the code modification.

First, replace the `TOKEN_YOUR_BOT` placeholder in the following lines with your bot's valid token:
```python
token = 'TOKEN_YOUR_BOT'
bot = telebot.TeleBot(token)
```

Now let's modify the code to avoid sending empty messages and handle any errors gracefully:

1. Update the `echo` handler by adding a check for empty messages before sending them.
2. Wrap the `bot.polling()` call in a try-except block to catch and log any uncaught exceptions.
3. Use `print()` or a logging library instead of raising exceptions when encountering unexpected errors.

Here's the updated code:

```python
import telebot
from telebot import ApiTelegramException
'''
# Your bot token
#token = 'TOKEN_YOUR_BOT'
#bot = telebot.TeleBot(token)

@bot.message_handler()
def echo(message):
    if message.text:  # Check for non-empty message before sending it
        bot.send_message(chat_id=message.chat.id, text=message.text)
    else:
        print('Ignoring empty message')

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(chat_id=message.chat.id, text='Привет!')
'''
if __name__ == '__main__':
    try:
        bot.polling()
    except ApiTelegramException as e:
        print('Caught ApiTelegramException:', e)
    except Exception as e:
        print('An unexpected error occurred:', e)
'''
'''
By checking for non-empty messages before sending them, you should be able to avoid sending empty messages and prevent the `Bad Request: message text is empty` error

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(chat_id=message.chat.id, text='Привет!')

@bot.message_handler()
def echo(message):
    bot.send_message(chat_id=message.chat.id, text=message.text)

if __name__ == '__main__':
    bot.polling()
```

Это простой пример кода Telegram бота на Python, который обрабатывает ошибку `ApiTelegramException: A request to the Telegram API was unsuccessful. Error code: 400. Description: Bad Request: message text is empty`. Когда такая ошибка выводится, мы печатаем сообщение для администратора бота и останавливаем работу бота, чтобы можно было исправить проблему с пустыми сообщениями. В реальном приложении необходимо найти источник появления пустых сообшений (токены могут быть закончены или код генерации сообщений имеет ошибку) и исправить их.
'''
# Получение задачи от пользователя или продолжение решения
@bot.message_handler(func=continue_filter)
def get_promt(message):
    user_id = str(message.from_user.id)  # ВАЖНО!
#   Проверка на тип сообщения (текст, картинка, видео и тд). Если это НЕ текст - сообщение об ошибке пользователю,
    if not message.text:
        bot.send_message(message.chat.id, "Необходимо отправить именно текстовое сообщение")
        # Cледующее сообщение пользователя попадает в эту же функцию - get_promt()
        bot.register_next_step_handler(message, get_promt)
        return
    # Получаем текст сообщения от пользователя
    user_request = message.text

    # if len(user_request) >= MAX_TOKENS:
    #     bot.send_message(user_id, "Запрос превышает количество символов\nИсправь запрос")
    #     bot.register_next_step_handler(message, get_promt)
    #     return

    # Проверка задачи пользователя на количество токенов. Если количество символов больше - сообщение об ошибке пользователю
    if gpt.count_tokens(user_request) >= gpt.MAX_TOKENS:
        bot.send_message(user_id, "Запрос превышает количество символов\nИсправь запрос")
        bot.register_next_step_handler(message, get_promt)
        return

    # Проверка: если у пользователя нет начатой задачи, тогда ее нужно начать
    if user_id not in users_history or users_history[user_id] == {}:
        if user_request == "Продолжить решение":
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

    # Пока что ответом от GPT будет любой текст, просто придумай его)
    # answer = "Позже здесь будет реальное решение, а пока что так :)"
    prompt = gpt.make_promt(users_history[user_id])
    resp = gpt.send_request(prompt)
    answer = resp.json()['choices'][0]['message']['content']

    # Дописываем этот ответ от GPT к предыдущему ответу GPT
    users_history[user_id]["assistant_content"] += answer
    save_to_json()

    # Отправляем полный ответ пользователю
    # Добавляем кнопки "продолжить решение" и "завершить решение".
    # Продолжить решение - пользователь просит GPT дописать ответ к текущей задаче
    # Завершить решение - решение задачи прекращается, все предыдущие сообщения удаляются из истории пользователя
    keyboard = create_keyboard(["Продолжить решение", "Завершить решение"])
    bot.send_message(message.chat.id, answer, reply_markup=keyboard)

# фильтр для обработки кнопочки "Завершить решение"
@bot.message_handler(commands=['end'])
@bot.message_handler(content_types=['text'], func=lambda message: message.text.lower() == "завершить решение")
def end_task(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Текущие решение завершено")
    users_history[user_id] = {}
    solve_task(message)

bot.polling()
