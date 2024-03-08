# channel_check.py
from aiogram import Bot
from aiogram.types import ChatMemberStatus

async def is_user_in_channel(bot: Bot, user_id: int, channel_username: str) -> bool:
    try:
        # Получаем информацию о пользователе в чате канала
        chat_member = await bot.get_chat_member(channel_username, user_id)
        # Проверяем статус пользователя
        return chat_member.status not in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED]
    except Exception as e:
        print(f"Ошибка при проверке подписки: {e}")
        return False