import os
import time

import requests
import telegram

import logging
from dotenv import load_dotenv

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

API_URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'

TIME_REPEAT_RESPONSE = 300
TIME_SLEEP = 5


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    if homework_name is None:
        return 'Нам не повезло, и нам пришли пустые данные'
    if homework.get('status') == 'reviewing':
        verdict = 'Ваша работа проходит ревью.'
    if homework.get('status') == 'approved':
        verdict = ('Ревьюеру всё понравилось,'
                   ' можно приступать к следующему уроку.')
    else:
        verdict = 'К сожалению в работе нашлись ошибки.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    if current_timestamp is None:
        return 'Server did not respond'
    headers = {
        'Authorization': f'OAuth {PRAKTIKUM_TOKEN}',
    }
    params = {
        'from_date': current_timestamp,
    }
    try:
        homework_statuses = requests.get(API_URL,
                                         params=params,
                                         headers=headers
                                         )
    except requests.HTTPError:
        logging.warning('Сервер не ответил')
        return 'Can\'t connect to the server'
    return homework_statuses.json()


def send_message(message, bot_client):
    try:
        str(message)
    except ValueError:
        logging.error('Бот не смог отправить сообщение.')
        return 'Message not sent. Please enter valid characters'
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                    new_homework.get('homeworks')[0]),
                    bot
                )
            current_timestamp = new_homework.get('current_date',
                                                 current_timestamp)
            time.sleep(TIME_REPEAT_RESPONSE)

        except Exception as error:
            print(f'Бот столкнулся с ошибкой: {error}')
            time.sleep(TIME_SLEEP)


if __name__ == '__main__':
    main()
