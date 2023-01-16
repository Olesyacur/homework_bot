## Проект homework_bot
Телеграм-бот для проверки статуса учебных проектов, сданных ревьюеру.

### Технологии

Python

Python-telegram-bot

### Запуск проекта

Для запуска проекта бота необходимо получить токен к API Практикум.Домашка по
адресу: https://oauth.yandex.ru/verification_code#access_token=y0_AgAAAAAOfSqaAAYckQAAAADY4xxHceeHbWerTrqNqg4k_plqLNOW8qg&token_type=bearer&expires_in=1719905
- Клонируйте проект
```
git clone git@github.com:Olesyacur/homework_bot.git
```
- Установите и активируйте виртуальное окружение
- Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
```
- Добавляем токены в файл .env:
PRACTICUM_TOKEN=токен API Практикум.Домашка
TELEGRAM_TOKEN=ваш телеграм токен
TELEGRAM_CHAT_ID=телеграм токен вашего бота

- В папке с файлом manage.py выполните команду:
```
python3 manage.py runserver
```
### Автор
Чурсина Олеся