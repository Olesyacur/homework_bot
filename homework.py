import os
# from urllib import response
import logging
import telegram
import requests
import time
# from telegram import Bot
# from http import HTTPStatus
# from telegram.ext import Updater, Filters, StreamHandler
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.DEBUG,
    filename='program.log', 
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(
    'my_logger.log',
    maxBytes=50000000,
    backupCount=5
)
logger.addHandler(handler)
def send_message(bot, message):
    bot.send_message(TELEGRAM_CHAT_ID, message)
    return


def get_api_answer(current_timestamp):
    timestamp = 0 # current_timestamp  or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    return response.json()


def check_response(response):
    result = response['homeworks']
    return result


def parse_status(homework):
    """Информация о конкретной домашней работе, статус этой работы."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    
    if homework_status in HOMEWORK_STATUSES:
        verdict = HOMEWORK_STATUSES[homework_status]
        return f'Есть изменения в {homework_name}". {verdict}'


def check_tokens():
    """Проверяет наличие всех кодов, паролей, ID, токенов."""
    secret_cods = {
        'practicum_token': PRACTICUM_TOKEN,
        'telegram_token': TELEGRAM_TOKEN,
        'telegram_chat_id': TELEGRAM_CHAT_ID,
    }
    for secret_cod, value in secret_cods.items():
        if not value:
            print(f'{secret_cod} отсутствует')
            return False
    return True



def main():
    """Основная логика работы бота."""
    if check_tokens():
        bot = telegram.Bot(token=TELEGRAM_TOKEN)

    while True:
        try:
            current_timestamp = 0 # int(time.time())
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            message = parse_status(homework[0])
            send_message(bot, message)
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            time.sleep(RETRY_TIME)

if __name__ == '__main__':
    main()
