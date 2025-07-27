import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.bot import DefaultBotProperties
from config import config
from db.database import init_db
from handlers import registation, admin, start, commands, news, chat, cashpostcreate, barterpostcreate
from utils import export


bot = Bot(
    token=config.bot_token,
    default=DefaultBotProperties(parse_mode="HTML")
)

dp = Dispatcher(storage=MemoryStorage())

dp.include_router(start.router_start)
dp.include_router(admin.router)


dp.include_router(commands.commands)
dp.include_router(export.base)
dp.include_router(news.newses)
dp.include_router(registation.router)
dp.include_router(cashpostcreate.cachbackpost)
dp.include_router(barterpostcreate.barterpost)
dp.include_router(chat.private)


async def main():
    print("🔧 Инициализация базы данных...")
    await init_db()

    print("🚀 Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
