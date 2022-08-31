import logging
import random
import os
import redis
from dotenv import load_dotenv
from os import listdir
from os.path import isfile, join


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
    folder_name = 'questions'
    files = [file for file in listdir(folder_name) if isfile(join(folder_name, file))]
    random_file = join(folder_name, random.choice(files))
    questions_and_answers = {}
    with open(random_file, 'r', encoding='KOI8-R') as file:
        full_text = file.read()
    sections = full_text.split('\n\n')
    for item in sections:
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


def get_redis_db():
    load_dotenv()
    return redis.Redis(
        host=os.getenv('REDIS_END_POINT'),
        port=os.getenv('REDIS_PORT'),
        password=os.getenv('REDIS_PASSWORD'),
    )    
