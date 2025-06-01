import telebot
import threading
import time
from telebot import types

TOKEN = 'ТВОЙ_ТОКЕН_БОТА'
bot = telebot.TeleBot(TOKEN)

# Список підтверджених користувачів
verified_users = set()

# Обробка /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("✅ Я людина", callback_data='verify')
    markup.add(button)
    bot.send_message(message.chat.id, "Щоб почати, підтверди, що ти людина:", reply_markup=markup)

# Обробка кнопки
@bot.callback_query_handler(func=lambda call: call.data == 'verify')
def verify_user(call):
    user_id = call.message.chat.id
    if user_id not in verified_users:
        verified_users.add(user_id)
        bot.send_message(user_id, "✅ Ти підтвердив, що людина.\nТвоя заявка прийнята.\nОчікуй нові повідомлення кожні 5 хвилин 😉")
    else:
        bot.send_message(user_id, "Ти вже підтвердив, що людина!")

# Фоновий потік з повідомленнями
def send_every_5_minutes():
    while True:
        for user_id in list(verified_users):
            try:
                bot.send_message(user_id, "🔞 Твоя доза вайфу вже тут. Не прогав!")
            except:
                continue
        time.sleep(300)  # 5 хвилин

# Запуск потоку
threading.Thread(target=send_every_5_minutes).start()

# Запуск бота
bot.polling(none_stop=True)
