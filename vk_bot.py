import logging
import os
import random

import redis
import telegram
import vk_api as vk
from dotenv import load_dotenv
from vk_api.keyboard import VkKeyboard
from vk_api.longpoll import VkEventType, VkLongPoll

from get_logger import TelegramLogsHandler
from get_quiz import get_quiz

logger = logging.getLogger('Logger')


def get_custom_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Новый вопрос')
    keyboard.add_button('Сдаться')
    keyboard.add_line()
    keyboard.add_button('Мой счет')
    return keyboard.get_keyboard()


def give_up(event, vk_api, r, quiz):
    question = r.get(event.user_id).decode()
    response = quiz[question]
    vk_api.messages.send(
        user_id=event.user_id,
        message=response,
        random_id=random.randint(1, 1000),
        keyboard=get_custom_keyboard(),
    )
    question = random.choice(list(quiz.keys()))
    r.set(event.user_id, question)
    vk_api.messages.send(
        user_id=event.user_id,
        message=question,
        random_id=random.randint(1, 1000),
        keyboard=get_custom_keyboard(),
    )


def send_question(event, vk_api, r, quiz):
    question = random.choice(list(quiz.keys()))
    r.set(event.user_id, question)
    vk_api.messages.send(
        user_id=event.user_id,
        message=question,
        random_id=random.randint(1, 1000),
        keyboard=get_custom_keyboard(),
    )


def handle_response(event, vk_api, r, quiz):
    question = r.get(event.user_id).decode()
    response = quiz[question]

    if event.text in response:
        text = 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
    else:
        text = 'Неправильно… Попробуешь ещё раз?'

    vk_api.messages.send(
        user_id=event.user_id,
        message=text,
        random_id=random.randint(1, 1000),
        keyboard=get_custom_keyboard(),
    )


def main():
    """Main function."""
    load_dotenv()
    logger_bot_token = os.getenv('LOGGER_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    logger_bot = telegram.Bot(logger_bot_token)
    logger.addHandler(TelegramLogsHandler(logger_bot, chat_id))
    logger.warning("VK бот запущен")

    r = redis.Redis(
        host=os.getenv('REDIS_END_POINT'),
        port=os.getenv('REDIS_PORT'),
        password=os.getenv('REDIS_PASSWORD'),
    )
    folder_name = os.getenv('FOLDER_NAME', default='questions')
    quiz = get_quiz(folder_name)

    vk_token = os.getenv('VK_API_KEY')
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == "Сдаться":
                give_up(event, vk_api, r, quiz)
            elif event.text == "Новый вопрос":
                send_question(event, vk_api, r, quiz)
            else:
                handle_response(event, vk_api, r, quiz)


if __name__ == "__main__":
    main()
