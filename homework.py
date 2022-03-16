import os
import time
import requests
import telegram
import logging

from dotenv import load_dotenv
from http import HTTPStatus

from exceptions import MessageError, StatusCodeError

load_dotenv()


PRACTICUM_TOKEN = os.getenv('MY_PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('MY_TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('MY_TELEGRAM_CHAT_ID')


RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Метод отправки сообщения."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.info('Сообщение отправлено')
    except telegram.error.TelegramError as error:
        logger.error(MessageError)
        raise MessageError('Сообщение не отправлено')


def get_api_answer(current_timestamp):
    """Метод запроса к API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != HTTPStatus.OK:
            logging.error(StatusCodeError)
            raise StatusCodeError('Данный ресурс недоступен')
        return response.json()
    except requests.RequestException as error:
        logging.error(error)
        raise requests.RequestException('Данный ресурс недоступен')


def check_response(response):
    """Метод проверки ответа API на корректность."""
    try:
        homeworks = response['homeworks']
    except KeyError:
        logger.error(KeyError)
        raise KeyError('Ключ недоступен')
    return homeworks


def parse_status(homework):
    """Метод проверки статуса домашней работы."""
    homework_name = homework.get('homework_name')
    if not homework_name:
        logger.error('Название отсутствует')
        raise Exception('Название отсутствует')
    homework_status = homework.get('status')
    verdict = HOMEWORK_STATUSES[homework_status]
    if verdict is None:
        logging.error('Неизвестный статус')
        raise KeyError()
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Метод проверки переменных окружения."""
    if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        return True
    else:
        return False


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    status_homework = None
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)[0]
            if status_homework != homework.get('status'):
                message = parse_status(homework)
                send_message(bot, message)
                status_homework = homework.get('status')
            else:
                logging.debug('Статус не изменился')
            current_timestamp = response.get('current_date')
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG,
    )
    main()
