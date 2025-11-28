import os
import telebot
from telebot import types
import gspread
from datetime import datetime
import time

# Конфигурация из переменных окружения
BOT_TOKEN = os.environ.get('BOT_TOKEN')
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID')

# Инициализация бота
bot = telebot.TeleBot(BOT_TOKEN)

# Подключение к Google Таблицам
# Файл clever.json должен быть создан из переменной окружения GOOGLE_CREDENTIALS
if os.environ.get('GOOGLE_CREDENTIALS'):
    with open('clever.json', 'w') as f:
        f.write(os.environ.get('GOOGLE_CREDENTIALS'))
    gc = gspread.service_account(filename='clever.json')
    wks = gc.open_by_key(SPREADSHEET_ID)
else:
    gc = None
    wks = None

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот для обращений Бурятия-инфо. Я работаю на Render! 🚀")

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Вы сказали: " + message.text)

if __name__ == "__main__":
    print("Бот запущен на Render!")
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(15)
