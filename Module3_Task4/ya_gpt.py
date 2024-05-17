import requests
import logging


logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(message)s")

TOKEN = ''
FOLDER_ID = ''

GPT_MODEL = 'yandexgpt'
# Ограничение на выход модели в токенах
MAX_MODEL_TOKENS = 100
# Креативность GPT (от 0 до 1)
MODEL_TEMPERATURE = 0.6


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


if __name__ == '__main__':
    result = ask_gpt('Блин, я совсем не знаю, как решать квадратные уравнения, объясни пж')
    print(result)

