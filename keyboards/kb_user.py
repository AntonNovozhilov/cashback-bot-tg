from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from config import (ADMIN_IDS, count_price_in_admin, count_users_in_admin,
                    home, kb_admin_pannel_text, kb_admin_text, kb_cannals_text,
                    kb_create_post_text, kb_faq_text, kb_price_text,
                    kb_requis_text, news)


def user_kb(user_telegram_id: int):
    """Главное меню."""
    kb = [
        [KeyboardButton(text=kb_cannals_text)],
        [
            KeyboardButton(text=kb_price_text),
            KeyboardButton(text=kb_create_post_text),
        ],
        [KeyboardButton(text=kb_requis_text)],
        [KeyboardButton(text=kb_faq_text), KeyboardButton(text=kb_admin_text)],
    ]
    if user_telegram_id in ADMIN_IDS:
        kb.append([KeyboardButton(text=kb_admin_pannel_text)])
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Воспользуйтесь меню или напишите админу сюда в чат",
    )
    return keyboard
