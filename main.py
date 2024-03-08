from aiogram import executor
from bot import dp
from start import register_handlers

async def on_startup(_):
    print('Бот запущен')

def main():
    register_handlers(dp)
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

if __name__ == '__main__':
    main()