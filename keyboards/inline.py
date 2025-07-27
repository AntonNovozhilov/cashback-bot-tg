from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def role_keyboard():
    role_buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Менеджер", callback_data="role_менеджер")],
            [InlineKeyboardButton(text="Селлер", callback_data="role_селлер")],
            [InlineKeyboardButton(text="Эксперт", callback_data="role_эксперт")],
        ])
    return role_buttons
    
def confirm_keyboard():
    confirm_buttons = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ OK", callback_data="confirm_ok")],
        [InlineKeyboardButton(text="🔁 Отмена", callback_data="confirm_restart")],
    ]) 
    return confirm_buttons


def moderation_keyboard(user_id: int):
    admin_buttons = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Разместить", callback_data=f"moderate_accept_{user_id}"),
            InlineKeyboardButton(text="❌ Отказать", callback_data=f"moderate_reject_{user_id}")
        ]
    ])
    return admin_buttons

def channel_post_keyboard(username: str) -> InlineKeyboardMarkup:
    channal_button = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💬 Написать", url=f"https://t.me/{username.lstrip('@')}"),
            InlineKeyboardButton(text="📥 Разместиться", url="https://t.me/seller_manager163_bot?start=add")  # заменить на юзернейм бота
        ]
    ])
    return channal_button

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def contact_keyboard() -> InlineKeyboardMarkup:
    contact =  InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Мой Telegram username", callback_data="contact_self")],
            [InlineKeyboardButton(text="✏ Указать другой контакт", callback_data="contact_custom")]
        ]
    )
    return contact


cancel_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Отменить", callback_data="cancel_post")]
])

skip_extra_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⏭ Пропустить", callback_data="skip_extra")]
    ]
)


def post_type_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📌 Резюме", callback_data="resume")],
        [InlineKeyboardButton(text="📣 Вакансия", callback_data="vacancy")],
    ])

def cancel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить", callback_data="confirm_restart")]
    ])

def skip_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пропустить", callback_data="skip_photo")]
    ])

def confirm_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Отправить", callback_data="confirm_ok"),
            InlineKeyboardButton(text="❌ Отменить", callback_data="confirm_restart")
        ]
    ])

def moderation_keyboard(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👍 Одобрить", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton(text="👎 Отклонить", callback_data=f"reject_{user_id}")
        ]
    ])


def type_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧑‍💼 Резюме", callback_data="type_resume")],
        [InlineKeyboardButton(text="🏢 Вакансия", callback_data="type_vacancy")],
    ])

def contact_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📌 Свой username", callback_data="contact_self")],
        [InlineKeyboardButton(text="✍️ Ввести вручную", callback_data="contact_custom")],
    ])

cancel_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="❌ Отменить", callback_data="confirm_restart")],
])

skip_photo_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Пропустить фото", callback_data="skip_photo")],
])

def finish_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Завершить", callback_data="finish_post")],
    ])

def confirm_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Всё верно", callback_data="confirm_ok"),
            InlineKeyboardButton(text="🔁 Начать заново", callback_data="confirm_restart"),
        ],
    ])

def moderation_keyboard(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👍 Одобрить", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton(text="✖️ Отклонить", callback_data=f"reject_{user_id}")
        ]
    ])

