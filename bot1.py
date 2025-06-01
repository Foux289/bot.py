import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

TOKEN = "ВАШ_ТОКЕН_БОТА"
ADMIN_CHAT_ID = 123456789  # ID админа или группы

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

user_requests = {}  # хранит статус заявки и подписки, например {user_id: {"approved": False, "subscribed": False}}

async def send_reminder(user_id):
    while True:
        user_data = user_requests.get(user_id)
        if user_data is None or user_data.get("subscribed"):
            # Если пользователь подтвердил подписку или заявки нет — останавливаем цикл
            break
        try:
            await bot.send_message(
                user_id,
                "Для подтверждения подпишись на: \nhttps://t.me/MidnightWaifus"
            )
        except Exception as e:
            print(f"Не удалось отправить сообщение {user_id}: {e}")
            break
        await asyncio.sleep(180)  # 180 секунд = 3 минуты

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton("Старт", callback_data="start_check"))
    await message.answer("Добро пожаловать! Нажмите кнопку, чтобы пройти проверку.", reply_markup=kb)
    user_requests[message.from_user.id] = {"approved": False, "subscribed": False}

@dp.callback_query_handler(lambda c: c.data == "start_check")
async def process_check(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Напишите, пожалуйста, 'Я человек', чтобы подтвердить, что вы не бот.")

@dp.message_handler(lambda message: message.text.lower() == "я человек")
async def handle_human(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Без username"
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("Принять", callback_data=f"accept_{user_id}"),
        InlineKeyboardButton("Отклонить", callback_data=f"reject_{user_id}")
    )
    await bot.send_message(ADMIN_CHAT_ID, f"Новая заявка от @{username} (ID: {user_id})", reply_markup=kb)
    await message.answer("Заявка отправлена на рассмотрение. Ожидайте ответа.")

@dp.callback_query_handler(lambda c: c.data.startswith("accept_") or c.data.startswith("reject_"))
async def process_admin_decision(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    data = callback_query.data
    user_id = int(data.split("_")[1])

    if data.startswith("accept_"):
        user_requests[user_id]["approved"] = True
        await bot.send_message(user_id, "Ваша заявка одобрена! Вот ссылка на закрытый канал: https://t.me/your_private_channel")
        # Запускаем цикл напоминаний
        asyncio.create_task(send_reminder(user_id))
        await bot.edit_message_text("Заявка одобрена", callback_query.message.chat.id, callback_query.message.message_id)
    elif data.startswith("reject_"):
        await bot.send_message(user_id, "К сожалению, ваша заявка отклонена.")
        await bot.edit_message_text("Заявка отклонена", callback_query.message.chat.id, callback_query.message.message_id)
        user_requests.pop(user_id, None)

@dp.message_handler(commands=['подтвердить'])
async def confirm_subscription(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_requests and user_requests[user_id].get("approved"):
        user_requests[user_id]["subscribed"] = True
        await message.answer("Спасибо за подтверждение подписки! Теперь уведомления больше приходить не будут.")
    else:
        await message.answer("Ваша заявка ещё не одобрена или вы не в списке.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
