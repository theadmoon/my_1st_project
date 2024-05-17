import telebot
import requests
import logging

# ��������� �����������
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="log_file.txt",
    filemode="w",
)

# ������ 'YOUR_TELEGRAM_BOT_TOKEN' �� ����� ������ ����
TOKEN = "6692081952:AAFi4pdTMmXpq-G1pCCdUwbu5Rn8il-Eeh4"
bot = telebot.TeleBot(TOKEN)

# ������� /start
@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    logging.info("�������� ��������������� ���������")
    bot.reply_to(
        message,
        "������! � ��� ��� �������� ����������� �������. ������� ��� ����� �����, � � ������ ����������� ������ �� ������ ����� ������.",
    )

# ��� ��������� ���������
@bot.message_handler()
def generate_robot(message):
    logging.debug(f"���������� ����� �� ������������: {message.text}")
    if not message.text:
        logging.warning("�������� ������ ��������� ���������")
        bot.reply_to(message, "����������, ������� ��� �����-������ �����.")
        return

    logging.info("��������� ����������� ������")
    url = f"https://robohash.org/{message.text}.png"
    response = requests.get(url)

    if response.status_code == 200:
        bot.send_photo(message.chat.id, photo=url)
        logging.info("����������� ������ ������� ����������")
    else:
        logging.error(
            f"�� ������� �������� ����������� ������, ��� ��������� {response.status_code}"
        )
        bot.reply_to(
            message,
            "������, � �� ���� ������������� ��� ���� ����������� ������ ����� ������.",
        )

@bot.message_handler(commands=['debug'])
def send_logs(message):
    with open("log_file.txt", "rb") as f:
        bot.send_document(message.chat.id, f)

if __name__ == "__main__":
    logging.info("��� �������")
    bot.infinity_polling()