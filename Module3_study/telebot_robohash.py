import telebot
import requests
import logging

# Настройка логирования
#logging.basicConfig(
#    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
#)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="log_file.txt",
    filemode="w",
)

# Замени 'YOUR_TELEGRAM_BOT_TOKEN' на токен твоего бота
TOKEN = "6692081952:AAFi4pdTMmXpq-G1pCCdUwbu5Rn8il-Eeh4"
bot = telebot.TeleBot(TOKEN)

# Команда /start
@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    logging.info("Отправка приветственного сообщения")
    bot.reply_to(
        message,
        "Привет! Я бот для создания изображений роботов. Отправь мне любой текст, и я создам изображение робота на основе этого текста.",
    )
@bot.message_handler(commands=["debug"])
def send_logs(message):
    with open("log_file.txt", "rb") as f:
        bot.send_document(message.chat.id, f)

# Все остальные сообщения
@bot.message_handler()
def generate_robot(message):
    logging.debug(f"Полученный текст от пользователя: {message.text}")
    if not message.text:
        logging.warning("Получено пустое текстовое сообщение")
        bot.reply_to(message, "Пожалуйста, отправь мне какой-нибудь текст.")
        return

    logging.info("Генерация изображения робота")
    url = f"https://robohash.org/{message.text}.png"
    response = requests.get(url)

    if response.status_code == 200:
        bot.send_photo(message.chat.id, photo=url)
        logging.info("Изображение робота успешно отправлено")
    else:
        logging.error(
            f"Не удалось получить изображение робота, код состояния {response.status_code}"
        )
        bot.reply_to(
            message,
            "Извини, я не смог сгенерировать для тебя изображение робота прямо сейчас.",
        )

if __name__ == "__main__":
    logging.info("Бот запущен")
    bot.infinity_polling()