from aiogram import Dispatcher

from handlers import (admin, barterpostcreate, cashpostcreate, chat, commands,
                      news, registation, start)
from utils import export


def main_router(dp: Dispatcher) -> None:
    dp.include_router(start.router_start)
    dp.include_router(admin.router)
    dp.include_router(commands.commands)
    dp.include_router(export.base)
    dp.include_router(news.newses)
    dp.include_router(registation.router)
    dp.include_router(cashpostcreate.cachbackpost)
    dp.include_router(barterpostcreate.barterpost)
    dp.include_router(chat.private)
