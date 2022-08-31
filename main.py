import logging
import os
import telegram
import random
import redis

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
from telegram import ReplyKeyboardMarkup
from dotenv import load_dotenv
from enum import IntEnum


logger = logging.getLogger('Logger')


class BotState(IntEnum):
    BUTTON_CHOICE, QUESTION, ANSWER = range(3)


class TelegramLogsHandler(logging.Handler):
    """Logger handler class."""

    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def get_questions_and_answers():
    questions_and_answers = {}
    with open('questions/1vs1201.txt', 'r', encoding='KOI8-R') as file:
        full_text = file.read()
    sections = full_text.split('\n\n\n')
    for section in sections:
        section_items = section.split('\n\n')
        for item in section_items:
            if item.startswith('Вопрос'):
                question = ' '.join(item.split('\n')[1:])
            elif item.startswith('Ответ'):
                answer = ' '.join(item.split('\n')[1:])
                if answer.endswith('.'):
                    answer = answer[:-1]
                if ' (' in answer:
                    answer = answer.split(' (')[0]
        questions_and_answers[question] = answer
    return questions_and_answers


def start(bot, update):
    custom_keyboard = [
        ['Новый вопрос', 'Сдаться'],
        ['Мой счет']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_text(
        'Привет! Я бот для викторин!', reply_markup=reply_markup)
    return BotState.BUTTON_CHOICE


def question(bot, update):
    question = random.choice(list(questions_and_answers.keys()))
    r.set(update.effective_chat.id, question)
    custom_keyboard = [
        ['Новый вопрос', 'Сдаться'],
        ['Мой счет']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(
        chat_id=update.effective_chat.id,
        text=question,
        reply_markup=reply_markup)
    return BotState.QUESTION


def response(bot, update):
    question = r.get(update.effective_chat.id).decode()
    response = questions_and_answers[question]

    if update.message.text in response:
        text = 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
    else:
        text = 'Неправильно… Попробуешь ещё раз?'

    custom_keyboard = [
        ['Новый вопрос', 'Сдаться'],
        ['Мой счет']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
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
    telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    logger_bot_token = os.getenv('LOGGER_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    logger_bot = telegram.Bot(logger_bot_token)
    logger.addHandler(TelegramLogsHandler(logger_bot, chat_id))
    logger.warning("Бот запущен")

    updater = Updater(telegram_bot_token)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            BotState.BUTTON_CHOICE: [RegexHandler('^Новый вопрос$', question)],
            BotState.QUESTION: [MessageHandler(Filters.text, response)],
        },
        fallbacks=[CommandHandler('cancel', done)]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    load_dotenv()
    r = redis.Redis(
        host=os.getenv('REDIS_END_POINT'),
        port=os.getenv('REDIS_PORT'),
        password=os.getenv('REDIS_PASSWORD'),
    )
    questions_and_answers = get_questions_and_answers()

    main()
