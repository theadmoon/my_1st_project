import os

from dotenv import load_dotenv

load_dotenv()

ADMINS_IDS = os.getenv('ADMINS_ID')
TG_TOKEN = os.getenv('TG_TOKEN')
FOLDER_ID = os.getenv('FOLDER_ID')
GPT_TOKEN = os.getenv('GPT_TOKEN')

TOKENIZER_URL = os.getenv('TOKENIZER_URL')
GPT_URL = os.getenv('GPT_URL')

GPT_MODEL = os.getenv('GPT_MODEL')

MAX_TOKENS_IN_SESSION = 500
MAX_TOKENS_FOR_ANSWER = 200
MAX_SESSIONS = 5
MAX_USERS = 3

HEADERS = {'Authorization': f'Bearer {GPT_TOKEN}'}
DEFAULT_DATA = {
    "modelUri": f"gpt://{FOLDER_ID}/{GPT_MODEL}/latest",
    "completionOptions": {
        "stream": False,
        "temperature": 0.7,
        "maxTokens": MAX_TOKENS_FOR_ANSWER
    },
}
