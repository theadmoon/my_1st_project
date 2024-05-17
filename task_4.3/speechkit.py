import requests


def speech_to_text(data):
    # iam_token, folder_id для доступа к Yandex SpeechKit
    iam_token = 't1.9euelZqJjMeTj8uNisqNjYuLl8vNne3rnpWaipLNno6az5yYnsedzIubmZnl8_cDT29N-e8FOmxP_d3z90N9bE357wU6bE_9zef1656Vmpycz5SXm5DOlpHPm8mVipbI7_zF656Vmpycz5SXm5DOlpHPm8mVipbIveuelZqKlpqMj5SPyo-VzYrKyJOOnrXehpzRnJCSj4qLmtGLmdKckJKPioua0pKai56bnoue0oye.y6ChBNX0hzIqZuAXoqclfVGl7r7U9ua_c_9Y3YUGPTnKVFgBSJ5z_E1jl5s0YCZs8nFYxZOZc_SihkpPwZTXAA'
    folder_id = 'b1ggs4ib73n9ij11a47v'

    # Указываем параметры запроса
    params = "&".join([
        "topic=general",  # используем основную версию модели
        f"folderId={folder_id}",
        "lang=ru-RU"  # распознаём голосовое сообщение на русском языке
    ])

    # Аутентификация через IAM-токен
    headers = {
        'Authorization': f'Bearer {iam_token}',
    }

    # Выполняем запрос
    response = requests.post(
        f"https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?{params}",
        headers=headers,
        data=data
    )

    # Читаем json в словарь
    decoded_data = response.json()
    # Проверяем, не произошла ли ошибка при запросе
    if decoded_data.get("error_code") is None:
        return True, decoded_data.get("result")  # Возвращаем статус и текст из аудио
    else:
        return False, "При запросе в SpeechKit возникла ошибка"


