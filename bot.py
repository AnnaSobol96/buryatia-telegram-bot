import os
import telebot
import gspread
from datetime import datetime
import time
import json

# Конфигурация из переменных окружения
BOT_TOKEN = os.environ.get('BOT_TOKEN')
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID')
GOOGLE_CREDENTIALS = os.environ.get('GOOGLE_CREDENTIALS')

bot = telebot.TeleBot(BOT_TOKEN)

# Создаем файл авторизации Google из переменной окружения
if GOOGLE_CREDENTIALS:
    try:
        # Записываем credentials в файл
        with open('clever.json', 'w') as f:
            f.write(GOOGLE_CREDENTIALS)
        print("✅ Файл clever.json создан из переменной окружения")
        
        # Подключаемся к Google Таблицам
        gc = gspread.service_account(filename='clever.json')
        spreadsheet = gc.open_by_key(SPREADSHEET_ID)
        print("✅ Подключение к Google Таблицам установлено")
        
    except Exception as e:
        print(f"❌ Ошибка создания clever.json: {e}")
else:
    print("❌ GOOGLE_CREDENTIALS не найдена")

# Районы
DISTRICTS = [
    "Кабанский", "Закаменский", "Бичурский", "Кяхтинский", "Муйский", 
    "Курумканский", "Мухоршибирский", "Тарбагатайский", "Тункинский", 
    "Окинский", "Селенгинский", "Джидинский", "Хоринский", "Кижингинский", 
    "Иволгинский", "Заиграевский", "Прибайкальский", "Баргузинский", 
    "Баунтовский", "Еравнинский", "г.Северобайкальск", "Северо-Байкальский",
    "НА ПЛАНЕРКУ ГЛАВЫ"
]

# Категории
CATEGORIES = [
    "Дороги", "Транспорт", "Госуслуги", "Благоустройство", "Иное", 
    "Здравоохранение", "Соц. защита", "Образование", "ЖКХ", "Энергетика", 
    "СВО, мобилизация", "Мусор", "Безопасность", "С/х и охота", 
    "Связь и информационные системы", "Культура", "Экономика", 
    "Экология, недра, лесхоз", "Физ. культура и спорт", "Труд и занятость", 
    "Строительство", "Общ- полит.вопросы", "Туризм"
]

# Хранилище для данных пользователей (в памяти)
user_data = {}

# Простой обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    welcome_text = f"""Привет, {user_name}! 👋

Я бот для обращений Бурятия-инфо.

Выберите район из списка ниже:"""
    
    # Создаем клавиатуру с районами
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    # Добавляем кнопки районов
    buttons = []
    for district in DISTRICTS:
        buttons.append(telebot.types.KeyboardButton(district))
    
    # Распределяем кнопки по рядам
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            keyboard.add(buttons[i], buttons[i+1])
        else:
            keyboard.add(buttons[i])
    
    # Сохраняем данные пользователя
    user_data[message.chat.id] = {'step': 'district'}
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=keyboard)

# Обработчик выбора района
@bot.message_handler(func=lambda message: message.text in DISTRICTS)
def handle_district(message):
    chat_id = message.chat.id
    district = message.text
    
    if chat_id not in user_data:
        user_data[chat_id] = {}
    
    user_data[chat_id]['district'] = district
    
    if district == "НА ПЛАНЕРКУ ГЛАВЫ":
        user_data[chat_id]['category'] = "Планерка"
        response = f"Вы выбрали: {district}\n\nОпишите ваше обращение:"
        user_data[chat_id]['step'] = 'text'
        
        # Убираем клавиатуру для ввода текста
        remove_keyboard = telebot.types.ReplyKeyboardRemove()
        bot.send_message(chat_id, response, reply_markup=remove_keyboard)
    else:
        # Показываем клавиатуру с категориями
        response = f"Вы выбрали район: {district}\n\nТеперь выберите категорию проблемы:"
        
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        buttons = []
        for category in CATEGORIES:
            buttons.append(telebot.types.KeyboardButton(category))
        
        for i in range(0, len(buttons), 2):
            if i + 1 < len(buttons):
                keyboard.add(buttons[i], buttons[i+1])
            else:
                keyboard.add(buttons[i])
        
        # Добавляем кнопку "Назад"
        keyboard.add(telebot.types.KeyboardButton("↩️ Назад к выбору района"))
        
        user_data[chat_id]['step'] = 'category'
        bot.send_message(chat_id, response, reply_markup=keyboard)

# Обработчик выбора категории
@bot.message_handler(func=lambda message: message.text in CATEGORIES)
def handle_category(message):
    chat_id = message.chat.id
    category = message.text
    
    if chat_id in user_data and 'district' in user_data[chat_id]:
        user_data[chat_id]['category'] = category
        user_data[chat_id]['step'] = 'text'
        
        response = f"Вы выбрали категорию: {category}\n\nТеперь опишите вашу проблему или обращение:"
        
        # Убираем клавиатуру для ввода текста
        remove_keyboard = telebot.types.ReplyKeyboardRemove()
        bot.send_message(chat_id, response, reply_markup=remove_keyboard)
    else:
        bot.send_message(chat_id, "Сначала выберите район!")

# Обработчик кнопки "Назад"
@bot.message_handler(func=lambda message: message.text == "↩️ Назад к выбору района")
def handle_back(message):
    chat_id = message.chat.id
    if chat_id in user_data:
        user_data[chat_id] = {'step': 'district'}
    
    send_welcome(message)

# Обработчик текстовых сообщений (обращения)
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    
    try:
        # Проверяем, ожидаем ли мы текст обращения
        if chat_id in user_data and user_data[chat_id].get('step') == 'text' and 'district' in user_data[chat_id] and 'category' in user_data[chat_id]:
            
            # Получаем данные пользователя
            district = user_data[chat_id]['district']
            category = user_data[chat_id]['category']
            appeal_text = message.text
            user_name = message.from_user.first_name
            
            # Записываем в таблицу
            current_month = datetime.now().strftime("%Y-%m")
            try:
                sheet = spreadsheet.worksheet(current_month)
            except:
                sheet = spreadsheet.add_worksheet(title=current_month, rows="1000", cols="6")
                sheet.append_row(["Дата и время", "Район", "Категория", "Текст обращения", "Имя", "Chat ID"])
            
            row_data = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                district,
                category,
                appeal_text,
                user_name,
                str(chat_id)
            ]
            
            sheet.append_row(row_data)
            
            # Отправляем подтверждение
            success_text = f"""✅ <b>Спасибо! Ваше обращение записано.</b>

<b>Район:</b> {district}
<b>Категория:</b> {category}
<b>Ваше обращение:</b> {appeal_text}

Для нового обращения отправьте /start"""
            
            bot.send_message(chat_id, success_text, parse_mode='HTML')
            
            # Очищаем данные пользователя
            if chat_id in user_data:
                del user_data[chat_id]
                
            # Уведомление администратору
            if ADMIN_CHAT_ID:
                admin_msg = f"""📝 <b>Новое обращение:</b>
👤 <b>Пользователь:</b> {user_name}
📍 <b>Район:</b> {district}
📂 <b>Категория:</b> {category}
💬 <b>Обращение:</b> {appeal_text[:100]}{'...' if len(appeal_text) > 100 else ''}"""
                
                bot.send_message(ADMIN_CHAT_ID, admin_msg, parse_mode='HTML')
                
        else:
            # Если это просто текст без контекста
            bot.send_message(chat_id, "Пожалуйста, используйте кнопки для выбора. Отправьте /start чтобы начать.")
            
    except Exception as e:
        print(f"Ошибка: {e}")
        bot.send_message(chat_id, "❌ Произошла ошибка при записи. Попробуйте позже.")

if __name__ == "__main__":
    print("🚀 Бот запускается...")
    
    # УДАЛЯЕМ ВЕБХУК ПЕРЕД ЗАПУСКОМ
    try:
        bot.remove_webhook()
        print("✅ Вебхук удален")
        time.sleep(1)
    except Exception as e:
        print(f"⚠️ Ошибка при удалении вебхука: {e}")
    
    print("🔄 Запускаем long polling...")
    
    # Запускаем бота с long polling
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(15)
            print("🔄 Перезапускаем бота...")
