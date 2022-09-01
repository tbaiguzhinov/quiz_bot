import logging
import os
import random
from enum import IntEnum

import telegram
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater, CallbackContext)

from bot_functions import (TelegramLogsHandler, get_questions_and_answers,
                           get_redis_db)

logger = logging.getLogger('Logger')


class BotState(IntEnum):
    BUTTON_CHOICE, QUESTION, ANSWER = range(3)


def get_custom_key_board():
    custom_keyboard = [
        ['Новый вопрос', 'Сдаться'],
        ['Мой счет']]
    return ReplyKeyboardMarkup(custom_keyboard)


def start(update: Update, context: CallbackContext):
    reply_markup = get_custom_key_board()
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Привет! Я бот для викторин!',
        reply_markup=reply_markup
    )
    return BotState.BUTTON_CHOICE


def handle_question_request(update: Update, context: CallbackContext):
    question = random.choice(list(questions_and_answers.keys()))
    r.set(update.effective_chat.id, question)
    reply_markup = get_custom_key_board()
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=question,
        reply_markup=reply_markup)
    return BotState.QUESTION


def handle_give_up(update: Update, context: CallbackContext):
    question = r.get(update.effective_chat.id).decode()
    response = questions_and_answers[question]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response,
    )
    question = random.choice(list(questions_and_answers.keys()))
    r.set(update.effective_chat.id, question)
    reply_markup = get_custom_key_board()
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=question,
        reply_markup=reply_markup)
    return BotState.QUESTION


def handle_response_attempt(update: Update, context: CallbackContext):
    question = r.get(update.effective_chat.id).decode()
    response = questions_and_answers[question]

    if update.message.text in response:
        text = 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
        reply_markup = get_custom_key_board()
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=reply_markup)
        return BotState.BUTTON_CHOICE
    else:
        text = 'Неправильно… Попробуешь ещё раз?'
        reply_markup = get_custom_key_board()
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=reply_markup)
        return BotState.QUESTION


def done(update: Update, context: CallbackContext):
    context.bot.send_message("Thank you!")
    return ConversationHandler.END


def error(update: Update, context: CallbackContext):
    logger.warning(
        f'Update {update} caused error {context.error},\
traceback {context.error.__traceback__}'
    )


def main(r, questions_and_answers):
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
                MessageHandler(Filters.regex('^Новый вопрос$'), handle_question_request),
            ],
            BotState.QUESTION: [
                MessageHandler(Filters.regex('^Сдаться$'), handle_give_up),
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
    main(r, questions_and_answers)
