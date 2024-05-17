import requests
from content import SYSTEM_PROMPT, users_info, CONTINUE_STORY, END_STORY, Roles, Modes
from config import DEFAULT_DATA, TOKENIZER_URL, HEADERS, GPT_URL


def get_gpt_answer(messages, mode):
    data = DEFAULT_DATA.copy()
    data['messages'] = []
    for message in messages:
        role, content = message

        prompt_additional = CONTINUE_STORY
        if mode == Modes.END:
            prompt_additional = END_STORY

        if role == Roles.USER:
            content += '. ' + prompt_additional

        data['messages'].append(
            {'role': role,
             'text': content}
        )

    resp = send_request('post', GPT_URL, data)
    result = resp['result']

    # Возвращаем текстовый ответ и количество токенов, затраченных на ответ
    return result['alternatives'][0]['message']['text'], result['usage']['completionTokens']


def create_system_prompt(chat_id):
    user_choices = users_info[chat_id]
    message = (f"\nНапиши ответ в стиле {user_choices['genre']} "
               f"от имени эксперта в лице {user_choices['char']}. "
               f"Вот настроение эксперта: \n{user_choices['setting']}. \n"
               "Начало должно быть коротким, 1-3 предложения.\n")

    return SYSTEM_PROMPT + message


def send_request(method, url, data):
    resp = requests.request(method, url, json=data, headers=HEADERS)
    return resp.json()


def count_tokens_in_text(text):
    data = DEFAULT_DATA.copy()
    data['text'] = text
    response = send_request('post', TOKENIZER_URL, data)
    return len(response['tokens'])
