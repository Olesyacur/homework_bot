import os
import logging
from xmlrpc.client import SERVER_ERROR
import telegram
import requests
import time
import sys

from http import HTTPStatus

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
        logger.exception('Сообщение не отправлено')
    except SERVER_ERROR:
        logger.error('Сеть недоступна.')


def get_api_answer(current_timestamp):
    """Запрос к эндпоинту API-сервиса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except Exception as error:
        raise Exception(f'Сетевые проблемы: {error}')
    if response.status_code != HTTPStatus.OK:
        raise HTTPResponseNon(
            f'Сайт не работает. Ошибка {response.status_code}'
        )
    return response.json()


def check_response(response):
    """Проверяем ответ API на корректность."""
    if not isinstance(response, dict):
        raise TypeError('Некорректный тип данных ответа.')

    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise TypeError('Некорректный тип данных домашек.')
    return homeworks


def parse_status(homework):
    """Информация о конкретной домашней работе, статус этой работы."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')

    if not homework_name:
        raise KeyError('Домашние работы не обнаружены')

    if homework_status not in HOMEWORK_STATUSES:
        logger.debug('Отсутствуют в ответе новые статусы')
        raise NoneNothing('Отсутствуют в ответе новые статусы')

    verdict = HOMEWORK_STATUSES[homework_status]

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет наличие всех кодов, паролей, ID, токенов."""
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID,))


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    if not check_tokens():
        logger.critical('Отсутствуют ключ(и) для выполнения программы.')
        sys.exit('Отсутствуют ключ(и) для выполнения программы.')
    while True:
        try:
            current_timestamp = int(time.time())
            response_homeworks = get_api_answer(current_timestamp)
            if response_homeworks:
                for response_homework in response_homeworks:
                    homework = check_response(response_homework)
                    message = parse_status(homework)
                    send_message(bot, message)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.exception(message)
            send_message(bot, message)
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
