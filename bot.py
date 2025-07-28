import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import config
from core.database import init_db
from handlers import (admin, barterpostcreate, cashpostcreate, chat, commands,
                      news, registation, start)
from routers import main_router
from utils import export

bot = Bot(
    token=config.bot_token, default=DefaultBotProperties(parse_mode="HTML")
)

dp = Dispatcher(storage=MemoryStorage())
dp.include_router(main_router)


async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
