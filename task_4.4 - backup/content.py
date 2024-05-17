from enum import Enum


class Roles(str, Enum):
    SYSTEM = 'system'
    USER = 'user'
    ASSISTANT = 'assistant'


class Modes(str, Enum):
    CONTINUE = 'continue'
    END = 'end'


users_info = {}

users_state = {}

CHARS = ['Райан Гослинг', 'Альберт Эйнштейн', 'Илон Маск', 'Шрек']
GENRES = ['Юмор', 'Сенен', 'Романтика']
SETTINGS = ['Стандарт', 'Злюка', 'Ласковый']

USERS_STATES_TEXT = ['char', 'genre', 'setting']

CONTENT = {
    'char': {
        'text': 'Выбери эксперта!',
        'buttons_text': CHARS
    },
    'genre': {
        'text': 'Выбери стиль ответа!',
        'buttons_text': GENRES
    },
    'setting': {
        'text': 'Выбери настроение эксперта',
        'buttons_text': SETTINGS
    }
}

CONTINUE_STORY = 'Продолжи ответ в 1-3 предложения и оставь интригу. Не пиши никакой пояснительный текст от себя'
END_STORY = 'Напиши последний ответ, сделай вывод. Не пиши никакой пояснительный текст от себя'

SYSTEM_PROMPT = (
    "Ты отвечаешь на вопросы пользователя. После получения ответа пользователь может уточнять вопрос "
    "Не пиши никакого пояснительного текста в начале, а просто логично продолжай ответ на вопрос"
)
