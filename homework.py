import os
# from urllib import response
import logging
import telegram
import requests
import time
import sys

# from telegram import Bot
from http import HTTPStatus

from telegram.ext import Updater, Filters
from logging.handlers import RotatingFileHandler

from exceptions import HTTPResponseNon, NoneNothing

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
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)

def send_message(bot, message):
    """Отправляем сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(f'В чат отправлено: {message}')
    except telegram.error.TelegramError:
        print('Сообщение не отправлено')
    return


def get_api_answer(current_timestamp):
    """Запрос к эндпоинту API-сервиса."""
    timestamp = current_timestamp  or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != HTTPStatus.OK:
            raise HTTPResponseNon(
                'Сайт не работает. Ошибка {response.status_code}')
    except Exception as error:
        logging.error(error, exc_info=True)

    return response.json()


def check_response(response):
    """Проверяем ответ API на корректность."""

    result = response.get('homeworks')
    if result == []:
        raise NoneNothing('Пока ничего нет.')
    
    status = response.get('homeworks')[0]['status']
    if status not in HOMEWORK_STATUSES:
            raise TypeError('Нет ключа homeworks')
    return result


def parse_status(homework):
    """Информация о конкретной домашней работе, статус этой работы."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    
    try:
        if homework_status in HOMEWORK_STATUSES:
            verdict = HOMEWORK_STATUSES[homework_status]
    except NoneNothing:
        logger.debug('Отсутствуют в ответе новые статусы')

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
            logger.critical(f'{secret_cod} отсутствует')
            return False
    return True



def main():
    """Основная логика работы бота."""
    if check_tokens():
        bot = telegram.Bot(token=TELEGRAM_TOKEN)

    while True:
        try:
            current_timestamp = int(time.time())
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            message = parse_status(homework[0])
            send_message(bot, message)
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
        finally:
            time.sleep(RETRY_TIME)

if __name__ == '__main__':
    main()
