import requests

def text_to_speech(text):
    # iam_token, folder_id для доступа к Yandex SpeechKit
    iam_token = 't1.9euelZqWls6VnsqPnZSQlpSNl82Xj-3rnpWaipLNno6az5yYnsedzIubmZnl8_cfZwFO-e8lZ2wa_t3z918Vf0357yVnbBr-zef1656VmpSdlZWVnYvOkomVksjMzseY7_zF656VmpSdlZWVnYvOkomVksjMzseYveuelZqVj8vHmoySjZGZx5rJzsnGnbXehpzRnJCSj4qLmtGLmdKckJKPioua0pKai56bnoue0oye.IEC1bo3uscJt5YTK2i-oP5vx7YQLIjXzhGynFgJLIws_fbP15hXcknw49GiYLc6tJfoM-5xyXF1np6cIu2YJCQ'
    folder_id = 'b1ggs4ib73n9ij11a47v'
    # Аутентификация через IAM-токен
    headers = {
        'Authorization': f'Bearer {iam_token}',
    }
    data = {
        'text': text,  # текст, который нужно преобразовать в голосовое сообщение
        'lang': 'ru-RU',  # язык текста - русский
        'voice': 'filipp',  # мужской голос Филиппа
        'folderId': folder_id,
    }
    # Выполняем запрос
    response = requests.post(
        'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize',
        headers=headers,
        data=data
    )
    if response.status_code == 200:
        return True, response.content  # возвращаем статус и аудио
    else:
        return False, "При запросе в SpeechKit возникла ошибка"