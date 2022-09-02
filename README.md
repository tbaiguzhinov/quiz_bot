# Бот для проведения викторин.

Бот создан для проведения викторин по уроку 4 "Проводим викторину" курса [Devman](https://dvmn.org).

Код задеплоен в Телеграмме [здесь](https://t.me/quiz_devman_tb_bot).

Код задеплоен в ВК [здесь](https://vk.com/public215676950).

## Запуск

- Скачайте код
- Установите зависимости командой  
```pip install -r requirements.txt```
- Скачайте [архив с вопросами](https://dvmn.org/media/modules_dist/quiz-questions.zip) и сохраните .txt файлы в папке `questions` рядом с файлами `tg_bot.py` и `vk_bot.py`. (В репозитории уже добавлены три файла в качестве примера)
- Запустите бот в Телеграмме командой  
```python3 tg_bot.py```
- Запустите бот в Вконтакте командой  
```python3 vk_bot.py```

## Переменные окружения

Для корректной работы кода, необходимы переменные окружения. Чтобы их определить, создайте файл `.env` рядом с `main.py` и запишите туда данные в таком формате: `ПЕРЕМЕННАЯ=значение`.

* `LOGGER_BOT_TOKEN` - токен Telegram бота для отображения логов.
* `TELEGRAM_CHAT_ID`- ваш ID в Телеграм. Чтобы его получить, напишите в Telegram боту @userinfobot.
* `TELEGRAM_BOT_TOKEN` - токен Telegram бота, в котором будет работать бот для викторин.
* `REDIS_END_POINT` - ссылка на базу данных Redis.
* `REDIS_PORT` - порт базы данных Redis.
* `REDIS_PASSWORD` - пароль для входа в базу данных Redis.
* `VK_API_KEY` - ключ API для группы в ВК.
* `FOLDER_NAME`(опциональная перменная, по умолчанию `questions`) - путь до папки с вопросами.

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).