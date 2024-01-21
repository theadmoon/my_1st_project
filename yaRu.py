import requests
result = requests.get("http://ya.ru")
print(result.text)

day = 14
month = 12
result = requests.get(f'http://numbersapi.com/{month}/{day}/date')
print(result.text)