# keyboards/admin.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
import os 
from dotenv import load_dotenv

load_dotenv('.env')

from config import ADMIN_IDS

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS



def admin_panel_keyboard():
    admin =  InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Скачать базу", callback_data="download_excel")]
    ])
    return admin


# def admin_rkb(user_tg_id: int):
#     admin = os.getenv('ADMIN_IDS')
#     if str(user_tg_id) in admin:
#         kb = [
#             [KeyboardButton(text='Админка')
#         ]]
#         keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True,)
#         return keyboard
    
def kb_admin(user_telegram_id: int):
    '''Меню в админке.'''
    kb = [
        [KeyboardButton(text='Скачать базу')],
        [KeyboardButton(text='Сделать рассылку')],
        [KeyboardButton(text='Статистика')],
        [KeyboardButton(text='Разместить пост в ВК')],
        [KeyboardButton(text='Выйти')]
    ]
    return ReplyKeyboardMarkup(keyboard=kb)