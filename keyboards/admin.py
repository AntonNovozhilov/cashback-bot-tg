import os

from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)
from dotenv import load_dotenv

load_dotenv(".env")

from config import ADMIN_IDS


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def admin_panel_keyboard():
    admin = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📥 Скачать базу", callback_data="download_excel"
                )
            ]
        ]
    )
    return admin


def kb_admin(user_telegram_id: int):
    """Меню в админке."""
    kb = [
        [KeyboardButton(text="Скачать базу")],
        [KeyboardButton(text="Сделать рассылку")],
        [KeyboardButton(text="Статистика")],
        [KeyboardButton(text="Разместить пост в ВК")],
        [KeyboardButton(text="Выйти")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb)
