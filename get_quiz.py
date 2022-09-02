import random
from os import listdir
from os.path import isfile, join


def get_questions_and_answers(folder_name):
    files = [file for file in listdir(
        folder_name) if isfile(join(folder_name, file))]
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
