import sqlite3

import requests
from transformers import AutoTokenizer
from config import *

import os
import json
import logging
import time

from config import GPT_MODEL, MAX_MODEL_TOKENS, MODEL_TEMPERATURE, SYSTEM_PROMT
#from info import CONTINUE_STORY, END_STORY

TOKEN_PATH = 'creds/gpt_token.json'
FOLDER_ID_PATH = 'creds/gpt_folder_id.txt'

# Подсчитывает количество токенов в сессии
#def count_tokens_in_dialogue(message: sqlite3.Row) -> int:
    # token =get_creds()
#    headers =
# Подсчитывает количество токенов в сессии
# messages - все промты из указанной сессии
def count_tokens_in_dialogue(messages: sqlite3.Row):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
       "modelUri": f"gpt://{folder_id}/yandexgpt-lite/latest",
       "maxTokens": MAX_MODEL_TOKENS,
       "messages": []
    }

        # Проходимся по всем сообщениям и добавляем их в список
    for row in messages:
        data["messages"].append(
            {
                "role": row["role"],
                "text": row["content"]
            }
        )

    return len(
        requests.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenizeCompletion",
            json=data,
            headers=headers
        ).json()["tokens"]
    )
def create_promt(user_data, user_id):
    promt = SYSTEM_PROMT
    promt += (f"\nНапиши начало истории в стиле {user_data[user_id]['genre']} "
              f"с главным героем {user_data[user_id]['hero']}. "
              f"Вот начальный сеттинг: \n{user_data[user_id]['setting']}. \n"
              "Начало должно быть коротким, 1-3 предложения. \n")
    if user_data[user_id]['additional_info']:
        promt += (f"Также пользователь попросил учесть "
                  f"следущую дополнительную информацию: {user_data[user_id]['additional_info']}")

    promt += "Не пиши никакие подсказки пользователю, что делать дальше. Он сам знает"
    return promt

# из видео
# Выполняем запрос к YandexGPT
def ask_gpt(collection, mode = 'continue'):
    iam_token = '< твой IAM-токен >'  # Токен для доступа к YandexGPT
    folder_id = '< твой Folder_id >'  # Folder_id для доступа к YandexGPT

    headers = {
        'Authorization': f'Bearer {iam_token}',
        'Content-Type': 'application/json'
    }
    data = {
        "modelUri": f"gpt://{folder_id}/yandexgpt-lite/latest",  # модель для генерации текста
        "completionOptions": {
            "stream": False,  # потоковая передача частично сгенерированного текста выключена
            "temperature": MODEL_TEMPERATURE,  # чем выше значение этого параметра, тем более креативными будут ответы модели (0-1)
            "maxTokens": MAX_MODEL_TOKENS  # максимальное число сгенерированных токенов, очень важный параметр для экономии токенов
        },
        "messages": []
    }

    for row in collection:
        content = row['content']

        # Добавляем дополнительный текст к сообщению пользователя в зависимости от режима
        if mode == 'continue' and row['role'] =='user':
            content += '\n' + CONTINUE_STORY
        elif mode == 'end' and row['role'] == 'user':
            content += '\n' + END_STORY

        data["messages"].append(
            {"role": row["role"],
             "text": content
             }
        )
    # Выполняем запрос к YandexGPT
    try:
        response = requests.post("https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
                                 headers=headers,
                                 json=data)
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


'''
# из Тренажера
import requests
# Выполняем запрос к YandexGPT
def ask_gpt(text):
    iam_token = '< твой IAM-токен >'  # Токен для доступа к YandexGPT
    folder_id = '< твой Folder_id >'  # Folder_id для доступа к YandexGPT

    headers = {
        'Authorization': f'Bearer {iam_token}',
        'Content-Type': 'application/json'
    }
    data = {
        "modelUri": f"gpt://{folder_id}/yandexgpt-lite",  # модель для генерации текста
        "completionOptions": {
            "stream": False,  # потоковая передача частично сгенерированного текста выключена
            "temperature": 0.6,  # чем выше значение этого параметра, тем более креативными будут ответы модели (0-1)
            "maxTokens": "200"  # максимальное число сгенерированных токенов, очень важный параметр для экономии токенов
        },
        "messages": [
            {
                "role": "user",  # пользователь спрашивает у модели
                "text": text  # передаём текст, на который модель будет отвечать
            }
        ]
    }
    # Выполняем запрос к YandexGPT
    try:
        response = requests.post("https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
                                 headers=headers,
                                 json=data)
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
    # Выполняем запрос к YandexGPT
    response = requests.post("https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
                             headers=headers,
                             json=data)

    # Проверяем, не произошла ли ошибка при запросе
    if response.status_code == 200:
                # достаём ответ YandexGPT
        text = response.json()["result"]["alternatives"][0]["message"]["text"]
        return text
    else:
        raise RuntimeError(
            'Invalid response received: code: {}, message: {}'.format(
                {response.status_code}, {response.text}
            )
        )
'''
class GPT:
    def __init__(self):
        self.URL = GPT_LOCAL_URL
        self.HEADERS = HEADERS
        self.MAX_TOKENS = MAX_TOKENS
        self.assistant_content = "Пишем класс на python: "

    # Подсчитываем количество токенов в промте
    @staticmethod
    def count_tokens(prompt):
        tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")  # название модели
        return len(tokenizer.encode(prompt))

    # Проверка ответа на возможные ошибки и его обработка
    def process_resp(self, response) -> [bool, str]:
        # Проверка статус кода
        if response.status_code < 200 or response.status_code >= 300:
            return False, f"Ошибка: {response.status_code}"

        # Проверка json
        try:
            full_response = response.json()
        except:
            return False, "Ошибка получения JSON"

        # Проверка сообщения об ошибке
        if "error" in full_response or 'choices' not in full_response:
            return False, f"Ошибка: {full_response}"

        # Результат
        result = full_response['choices'][0]['message']['content']

        # Пустой результат == объяснение закончено
        if result == "":
            return True, "Конец объяснения"

        return True, result

    # Формирование промта
    def make_promt(self, user_history):
        json = {
            "messages": [
                {"role": "system", "content": user_history['system_content']},
                {"role": "user", "content": user_history['user_content']},
                {"role": "assistant", "content": user_history['assistant_content']}
            ],
            "temperature": 0.1,
            "max_tokens": self.MAX_TOKENS,
        }
        return json

    # Отправка запроса
    def send_request(self, json):
        resp = requests.post(url=self.URL, headers=self.HEADERS, json=json)
        return resp

    # Сохраняем историю общения
    def save_history(self, assistant_content, content_response):
        return f"{assistant_content} {content_response}"