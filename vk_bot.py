import random
import os
import telegram
from dotenv import load_dotenv

import vk_api as vk
from vk_api.keyboard import VkKeyboard
from vk_api.longpoll import VkLongPoll, VkEventType

from bot_functions import get_questions_and_answers, get_redis_db, TelegramLogsHandler

logger = logging.getLogger('Logger')


def get_custom_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Новый вопрос')
    keyboard.add_button('Сдаться')
    keyboard.add_line()
    keyboard.add_button('Мой счет')
    return keyboard.get_keyboard()


def give_up(event, vk_api):
    vk_api.messages.send(
        user_id=event.user_id,
        message=event.text,
        random_id=random.randint(1, 1000),
        keyboard=get_custom_keyboard(),
    )


def send_question(event, vk_api):
    vk_api.messages.send(
        user_id=event.user_id,
        message=event.text,
        random_id=random.randint(1, 1000),
        keyboard=get_custom_keyboard(),
    )


def handle_response(event, vk_api):
    vk_api.messages.send(
        user_id=event.user_id,
        message=event.text,
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

    vk_token = os.getenv('VK_API_KEY')
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == "Сдаться":
                give_up(event, vk_api)
            elif event.text == "Новый вопрос":
                send_question(event, vk_api)
            else:
                handle_response(event, vk_api)


if __name__ == "__main__":
    main()
