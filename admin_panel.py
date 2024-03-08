# admin_panel.py
from aiogram import Bot, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import Database
from bot import bot, dp

db = Database('database.db')

# Функция для создания клавиатуры админ-панели
def admin_panel_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton(text='Количество пользователей', callback_data='user_count'),
        InlineKeyboardButton(text='Последние 10 пользователей', callback_data='last_users'),
        InlineKeyboardButton(text='Топ 10 пользователей', callback_data='top_users'),
    ]
    keyboard.add(*buttons)
    return keyboard

# Обработчик команды /admin
async def admin_panel(message: types.Message):
    if message.from_user.id == ADMIN_USER_ID:
        keyboard = admin_panel_keyboard()
        await message.answer('Админ-панель', reply_markup=keyboard)
    else:
        await message.answer('У вас нет прав доступа к админ-панели')

# Обработчик нажатия на кнопки админ-панели
async def process_callback_button(callback_query: types.CallbackQuery):
    if callback_query.from_user.id == ADMIN_USER_ID:
        if callback_query.data == 'user_count':
            user_count = get_user_count()
            await callback_query.message.bot.answer_callback_query(callback_query.id, f'Общее количество пользователей: {user_count}')
        elif callback_query.data == 'last_users':
            last_users = get_last_users(10)
            user_info = '\n'.join([f'{user.id}: {user.username}' for user in last_users])
            await callback_query.message.bot.answer_callback_query(callback_query.id, f'Последние 10 пользователей:\n{user_info}')
    else:
        await callback_query.message.bot.answer_callback_query(callback_query.id, 'У вас нет прав доступа к этой функции')

# Обработчик кнопки для получения топ 10 пользователей
@dp.callback_query_handler(lambda c: c.data == 'top_users')
async def top_users_button_handler(callback_query: types.CallbackQuery):
    top_users = db.get_top_users()
    message = "Топ 10 пользователей по количеству полученных вопросов:\n\n"
    for index, user in enumerate(top_users, start=1):
        message += f"{index}. @{user[1]} ({user[2]} вопросов)\n"
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, message)

def get_user_count():
    return db.get_user_count()

def get_last_users(n):
    return db.get_last_users(n)

# Константа для ID администратора
ADMIN_USER_ID = 2085376749  # Замените YOUR_ADMIN_USER_ID на ID администратора