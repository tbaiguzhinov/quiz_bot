import logging
import os
import telegram
import random

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
from telegram import ReplyKeyboardMarkup
from dotenv import load_dotenv
from enum import IntEnum

from bot_functions import get_questions_and_answers, get_redis_db, TelegramLogsHandler

logger = logging.getLogger('Logger')

class BotState(IntEnum):
    BUTTON_CHOICE, QUESTION, ANSWER = range(3)


def get_custom_key_board():
    custom_keyboard = [
        ['Новый вопрос', 'Сдаться'],
        ['Мой счет']]
    return ReplyKeyboardMarkup(custom_keyboard)


def start(bot, update):
    reply_markup = get_custom_key_board()
    update.message.reply_text(
        'Привет! Я бот для викторин!', reply_markup=reply_markup)
    return BotState.BUTTON_CHOICE


def handle_question_request(bot, update):
    question = random.choice(list(questions_and_answers.keys()))
    r.set(update.effective_chat.id, question)
    reply_markup = get_custom_key_board()
    bot.send_message(
        chat_id=update.effective_chat.id,
        text=question,
        reply_markup=reply_markup)
    return BotState.QUESTION


def handle_give_up(bot, update):
    question = r.get(update.effective_chat.id).decode()
    response = questions_and_answers[question]
    bot.send_message(
        chat_id=update.effective_chat.id,
        text=response,
    )
    question = random.choice(list(questions_and_answers.keys()))
    r.set(update.effective_chat.id, question)
    reply_markup = get_custom_key_board()
    bot.send_message(
        chat_id=update.effective_chat.id,
        text=question,
        reply_markup=reply_markup)
    return BotState.QUESTION


def handle_response_attempt(bot, update):
    question = r.get(update.effective_chat.id).decode()
    response = questions_and_answers[question]

    if update.message.text in response:
        text = 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
    else:
        text = 'Неправильно… Попробуешь ещё раз?'

    reply_markup = get_custom_key_board()
    bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=reply_markup)
    return BotState.BUTTON_CHOICE


def done(bot, update):
    update.message.reply_text("Thank you!")
    return ConversationHandler.END


def error(bot, update, error):
    logger.warning(f'Error encountered: {error}')


def main():
    """Main function."""
    load_dotenv()
    telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    logger_bot_token = os.getenv('LOGGER_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    logger_bot = telegram.Bot(logger_bot_token)
    logger.addHandler(TelegramLogsHandler(logger_bot, chat_id))
    logger.warning("Телеграм бот запущен")

    updater = Updater(telegram_bot_token)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            BotState.BUTTON_CHOICE: [
                RegexHandler('^Новый вопрос$', handle_question_request),
            ],
            BotState.QUESTION: [
                RegexHandler('^Сдаться$', handle_give_up),
                MessageHandler(Filters.text, handle_response_attempt)
            ],
        },
        fallbacks=[CommandHandler('cancel', done)]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    r = get_redis_db()
    questions_and_answers = get_questions_and_answers()
    main()
