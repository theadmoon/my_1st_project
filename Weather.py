import requests

url = 'https://api.weather.yandex.ru/v2/forecast'

# координаты места для предсказания погоды
params = {
    'lat': 43.2567,
    'lon': 76.9286
}

# указываем в запросе токен
token = "6c560976-16db-473f-aff6-30a7a0e32944" # ненастоящий токен

headers = {
    'X-Yandex-API-Key': token
}

response = requests.get(url, params=params, headers=headers)