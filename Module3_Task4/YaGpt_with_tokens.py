import requests
import logging
from transformers import AutoTokenizer


logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(message)s")

TOKEN = ''
FOLDER_ID = ''

GPT_MODEL = 'yandexgpt'
# Ограничение на выход модели в токенах
MAX_MODEL_TOKENS = 200
# Креативность GPT (от 0 до 1)
MODEL_TEMPERATURE = 0.6


# Раньше было так
# def count_tokens(prompt):
#     tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")  # название модели
#     return len(tokenizer.encode(prompt))


# Теперь подсчитывать токены необходимо вот так
def count_tokens(text: str) -> int:
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }
    a = len(
        requests.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenize",
            json={"modelUri": f"gpt://{FOLDER_ID}/yandexgpt/latest", "text": text},
            headers=headers
        ).json()['tokens']
    )
    return a


def ask_gpt(user_text):
    """Запрос к Yandex GPT"""

    url = f"https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }

    data = {
        "modelUri": f"gpt://{FOLDER_ID}/{GPT_MODEL}/latest",
        "completionOptions": {
            "stream": False,
            "temperature": MODEL_TEMPERATURE,
            "maxTokens": MAX_MODEL_TOKENS
        },
        "messages": [
            {"role": "system", "text": "Ты дружелюбный помощник для решения задач по математике"},
            {"role": "user", "text": user_text},
            # Можно продолжить диалог
            # {"role": "assistant", "text": ""}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            logging.debug(f"Response {response.json()} Status code:{response.status_code} Message {response.text}")
            result = f"Status code {response.status_code}. Подробности см. в журнале."
            return result
        result = response.json()['result']['alternatives'][0]['message']['text']
        logging.info(f"Request: {response.request.url}\n"
                     f"Response: {response.status_code}\n"
                     f"Response Body: {response.text}\n"
                     f"Processed Result: {result}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        result = "Произошла непредвиденная ошибка. Подробности см. в журнале."

    return result

# Анализ комментариев в социальных сетях.
#
# Запроси несколько сообщений в терминале
# Посчитай количество токенов в каждом
# Просуммируй токены всех сообщений пользователя
# Выдай ошибку “Вы превысили лимит”, как только пользователь выйдет суммарно за 50 токенов

if __name__ == '__main__':
    result = ask_gpt('Блин, я совсем не знаю, как решать квадратные уравнения, объясни пж')
    print(result)

    # Теперь считаем токены
    text_for_tokens = 'Это пробный текст. Хочу, чтобы мне вернулось количество токенов из которых он состоит'
    tokens = count_tokens(text_for_tokens)
    print(f'Количество токенов в тексте - {tokens}')


