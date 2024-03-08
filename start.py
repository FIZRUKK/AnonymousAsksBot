# start.py

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database import Database
from referral import get_referral_link
from bot import bot, dp
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters import CommandStart
from channel_check import is_user_in_channel
from aiogram.utils.callback_data import CallbackData
from admin_panel import admin_panel, process_callback_button
from config import ADMIN_ID



# Инициализация базы данных
db = Database('database.db')
ADMIN_USER_ID = ADMIN_ID
# Определение состояний для машины состояний aiogram
class UserStates(StatesGroup):
    waiting_for_question = State()


# Обработчик команды /start
@dp.message_handler(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    # Проверка, есть ли пользователь в базе данных
    if not db.user_exists(user_id):
        # Добавление нового пользователя в базу данных
        db.add_user(user_id, username, first_name, last_name)

    # Проверка, есть ли реферальный код в команде
    referral_code = message.get_args()
    if referral_code:
        # Поиск пользователя по реферальному коду
        referred_user = db.get_user_by_id(referral_code)
        
        if referred_user:
            # Сохранение информации о реферале
            share_link_keyboard = create_share_link_keyboard()
            await message.answer_sticker('CAACAgIAAxkBAAED-M5l6w2tQgRTfQKRkofQAAEjw0k1ZgMAApkMAAI_VAFKz5MMeWvBIpQ0BA')
            await message.answer(f"Привет, {first_name}! Скорее задай свой анонимный вопрос {referred_user[2]}", reply_markup=share_link_keyboard)
            await UserStates.waiting_for_question.set()
            # Сохранение реферального кода в состоянии пользователя
            await state.update_data(referral_code=referral_code)
        else:
            await message.answer_sticker('CAACAgIAAxkBAAED-NBl6w3N6wIpMHmrbbSuIgZRFhFUSQAC8wADVp29Cmob68TH-pb-NAQ')
            await message.answer("Неверный реферальный код.", reply_markup=share_link_keyboard)
    else:
        # Отправка сообщения с реферальной ссылкой
        share_link_keyboard = create_share_link_keyboard()
        await message.answer_sticker('CAACAgIAAxkBAAED-MZl6wxRkdAtY7Mcr1CVCVGB_fJDDwACiwEAAiteUwujYbxpJDSDUDQE')
        await message.answer(f"Привет-Привет {first_name}!\n\nНажми на кнопочку ниже, чтобы поделиться своей ссылкой, чтобы другие смогли задать тебе анонимные вопросики)", reply_markup=share_link_keyboard)



@dp.message_handler(state=UserStates.waiting_for_question)
async def process_question(message: types.Message, state: FSMContext):
    # Получение реферального кода из состояния пользователя
    data = await state.get_data()
    referral_code = data.get('referral_code')

    # Получение пользователя, который привел текущего пользователя
    referral_user_id = referral_code

    if referral_user_id and referral_user_id != message.from_user.id:
        # Отправка сообщения пользователю, который привел текущего пользователя
        await bot.send_message(referral_user_id, f"У тебя новый вопросик!\n\n{message.text}")

    # Отправка ответа на вопрос анонимно
    await message.answer_sticker('CAACAgIAAxkBAAED-NZl6w4mtlBb0zwc9uLlNBFKuRANhwACDQEAAladvQpG_UMdBUTXlzQE')
    share_link_keyboard = create_share_link_keyboard()
    await message.answer("Успешно отправлено!", reply_markup=share_link_keyboard)

    # Увеличение количества вопросов для пользователя в базе данных
    db.increment_question_count(message.from_user.id)

    await state.finish()

def create_share_link_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    share_link_button = KeyboardButton("Поделиться своей ссылкой")
    keyboard.add(share_link_button)
    return keyboard




# CallbackData для кнопок
subscribe_callback = CallbackData('subscribe', 'action')

# Функция для создания клавиатуры с кнопками подписки и проверки подписки
def create_subscribe_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    subscribe_button = InlineKeyboardButton('Подписаться на канал', url='https://t.me/DaniilGrebnevChannel')
    check_subscription_button = InlineKeyboardButton('Проверить подписку', callback_data=subscribe_callback.new(action='check'))
    keyboard.add(subscribe_button, check_subscription_button)
    return keyboard

# Обработчик нажатия на кнопку "Поделиться ссылкой"
async def share_link_button_handler(message: types.Message):
    channel_username = '@DaniilGrebnevChannel'  # Замените на название вашего канала
    user_id = message.from_user.id
    is_subscribed = await is_user_in_channel(bot, user_id, channel_username)
    if is_subscribed:
        referral_link = get_referral_link(user_id)
        await message.answer_sticker('CAACAgIAAxkBAAED-Nxl6w6YD5BT_PLz7V9cFnVIMCFTdQACEwADwDZPE6qzh_d_OMqlNAQ')
        await bot.send_message(user_id, f"Твоя ссылочка:\n\n{referral_link}")
    else:
        keyboard = create_subscribe_keyboard()
        await message.answer_sticker('CAACAgIAAxkBAAED-N5l6w7Yl7qz_RPjmyeOxgxEPnbSCQAC9wADVp29CgtyJB1I9A0wNAQ')
        await bot.send_message(user_id, "Чтобы получить свою ссылку, подпишись на наш канальчик", reply_markup=keyboard)
    
# Обработчик нажатия на кнопку подписки или проверки подписки
@dp.callback_query_handler(subscribe_callback.filter(action='check'))
async def check_subscription_callback_handler(query: types.CallbackQuery):
    user_id = query.from_user.id
    channel_username = '@DaniilGrebnevChannel'  # Замените на название вашего канала

    is_subscribed = await is_user_in_channel(bot, user_id, channel_username)
    if is_subscribed:
        referral_link = get_referral_link(user_id)
        await bot.send_message(user_id, f"Твоя реферальная ссылочка:\n\n{referral_link}")
    else:
        keyboard = create_subscribe_keyboard()
        await bot.send_message(user_id, "Ты все ещё не подписан на тгк...", reply_markup=keyboard)

    # Удаление сообщения с кнопками после нажатия
    await query.message.delete()
        
# Функция для регистрации обработчиков
def register_handlers(dp):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(process_question, state=UserStates.waiting_for_question)
    dp.register_message_handler(share_link_button_handler, text="Поделиться своей ссылкой")
    # Инициализация обработчиков из admin_panel.py
    dp.register_message_handler(admin_panel, commands=['admin'])
    dp.register_callback_query_handler(process_callback_button)
        