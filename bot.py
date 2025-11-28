import os
import telebot
from telebot import types
import gspread
from datetime import datetime, timedelta
import time
from threading import Lock
import json

# Получаем токен из переменных окружения
BOT_TOKEN = os.environ.get('BOT_TOKEN')

if not BOT_TOKEN:
    raise Exception("Не задан BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

# Подключение гугл-таблицы через переменные окружения
try:
    # Пытаемся получить учетные данные из переменных окружения
    google_credentials = {
        "type": os.environ.get('TYPE'),
        "project_id": os.environ.get('PROJECT_ID'),
        "private_key_id": os.environ.get('PRIVATE_KEY_ID'),
        "private_key": os.environ.get('PRIVATE_KEY', '').replace('\\n', '\n'),
        "client_email": os.environ.get('CLIENT_EMAIL'),
        "client_id": os.environ.get('CLIENT_ID'),
        "auth_uri": os.environ.get('AUTH_URI', 'https://accounts.google.com/o/oauth2/auth'),
        "token_uri": os.environ.get('TOKEN_URI', 'https://oauth2.googleapis.com/token'),
        "auth_provider_x509_cert_url": os.environ.get('AUTH_PROVIDER_CERT_URL', 'https://www.googleapis.com/oauth2/v1/certs'),
        "client_x509_cert_url": os.environ.get('CLIENT_CERT_URL')
    }

    # Проверяем, что все необходимые поля заполнены
    if not google_credentials["private_key"]:
        raise Exception("Не заданы учетные данные для Google Sheets")

    gc = gspread.service_account_from_dict(google_credentials)
    wks = gc.open("google-api-sheets-incident")
    print("Успешное подключение к Google Sheets")
except Exception as e:
    print(f"Ошибка подключения к Google Sheets: {e}")
    wks = None

# ... остальной код без изменений ...
