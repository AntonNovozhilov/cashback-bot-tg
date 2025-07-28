import asyncio
from collections import defaultdict

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select

from config import ADMIN_IDS, KANAL
from core.database import async_session
from fsm.states import PostBarter
from handlers.cashpostcreate import contains_emoji
from keyboards.inline_kb import finish_kb2
from keyboards.kb_user import user_kb
from models.models import ChatPrivatUser

barterpost = Router()

media_group_bufferbarter = defaultdict(list)


async def chat_privat(tg_id):
    """Список чатов."""
    async with async_session() as session:
        result = await session.scalars(
            select(ChatPrivatUser.user_id).where(
                ChatPrivatUser.user_id == tg_id
            )
        )
        return result.all()


def escape_md(text: str) -> str:
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    for ch in escape_chars:
        text = text.replace(ch, f"\\{ch}")
    return text


def barter_money_kb():
    """Клавиатура на 2ом шаге."""
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="С доплатой", callback_data="money_yes"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="Без доплаты", callback_data="money_no"
                )
            ],
        ]
    )


def home():
    """Кнопка для выхода в главное меню."""
    return types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="В главное меню")]],
        resize_keyboard=True,
        input_field_placeholder="Следуйте инструкции",
    )


@barterpost.callback_query(F.data == "create_barter")
async def start_post(callback: types.CallbackQuery, state: FSMContext):
    """Инициализация ввода названия товара."""
    await state.set_state(PostBarter.title)
    await callback.message.delete()
    await callback.message.answer(
        "Введите название товара", reply_markup=home()
    )


@barterpost.message(F.text == "В главное меню")
async def main_menu(message: types.Message, state: FSMContext):
    """Обработка нажатия на кнопку главное меню."""

    await state.clear()
    await message.answer(
        "Вы вернулись в главное меню",
        reply_markup=user_kb(message.from_user.id),
    )


@barterpost.message(PostBarter.title)
async def start_post2(message: types.Message, state: FSMContext):
    """Сохранение названия, запрос следующего состояния."""
    await state.update_data(title=message.text)
    if contains_emoji(message.text):
        await message.answer(
            "Пожалуйста, не используйте смайлики, только текст."
        )
        return
    await state.set_state(PostBarter.money)
    await message.answer(
        "Рассматриваете бартер с доплатой или без?",
        reply_markup=barter_money_kb(),
    )


@barterpost.callback_query(F.data.startswith("money_"))
async def set_money(callback: types.CallbackQuery, state: FSMContext):
    """Сохранение доплаты, запрос следующего состания."""
    money_value = (
        "С ДОПЛАТОЙ" if callback.data == "money_yes" else "БЕЗ ДОПЛАТЫ"
    )
    await state.update_data(money=money_value)
    await callback.message.answer(
        "Укажите основные критерии блогера (Напрмер, соцсеть, кол-во охватов, тематика и т.д.):",
        reply_markup=home(),
    )
    await state.set_state(PostBarter.web)


@barterpost.message(PostBarter.money)
async def block_text_input_on_money(message: types.Message):
    """Обработка отправки сообщения, где нужно только нажать на кнопку."""
    await message.answer("❗️Пожалуйста, выберите вариант, нажав кнопку выше ☝️")


@barterpost.message(PostBarter.web)
async def criteria(message: types.Message, state: FSMContext):
    """Сохранение критериев, запрос следующего состания."""
    await state.update_data(web=message.text)
    await message.answer(
        "Опишите задание (Например, Снять рилс, выложить сториз, выкупить по ТЗ и т.д.):",
        reply_markup=home(),
    )
    await state.set_state(PostBarter.descriptions)


@barterpost.message(PostBarter.descriptions)
async def set_description(message: types.Message, state: FSMContext):
    """Сохранение задания, запрос следующего состания."""
    await state.update_data(descriptions=message.text)
    await message.answer("Контакт для связи:", reply_markup=home())
    await state.set_state(PostBarter.seller)


@barterpost.message(PostBarter.seller)
async def set_seller(message: types.Message, state: FSMContext):
    """Сохранение контакта, запрос следующего состания."""
    await state.update_data(seller=message.text)
    await message.answer(
        "Теперь прикрепите фото к посту:", reply_markup=home()
    )
    await state.set_state(PostBarter.photo)


@barterpost.message(PostBarter.photo, ~F.photo)
async def wrong_input_in_photobarter(message: types.Message):
    """Обработка загрузки не фотографии."""
    await message.answer(
        "❗️Пожалуйста, прикрепите *фотографию* товара.\n"
        "Это можно сделать, используя 📎 и выбрав *Фото*.\n"
    )


@barterpost.message(PostBarter.photo, F.photo)
async def post_photo(message: types.Message, state: FSMContext):
    """Добавление фотографий для отправки."""
    if message.media_group_id:
        media_group_bufferbarter[message.media_group_id].append(
            message.photo[-1].file_id
        )
        if len(media_group_bufferbarter[message.media_group_id]) == 1:
            await asyncio.sleep(1.5)
            photo_ids = media_group_bufferbarter.pop(message.media_group_id)
            data = await state.get_data()
            photos = data.get("photos", [])
            photos.extend(photo_ids)
            await state.update_data(photos=photos)
            await message.answer(
                "🖼 Фото добавлены. Далее: отправьте ещё или нажмите кнопку ниже для завершения.",
                reply_markup=finish_kb2(),
            )
    else:
        data = await state.get_data()
        photos = data.get("photos", [])
        photos.append(message.photo[-1].file_id)
        await state.update_data(photos=photos)
        await message.answer(
            "🖼 Фото добавлены. Далее: отправьте ещё или нажмите кнопку ниже для завершения.",
            reply_markup=finish_kb2(),
        )


@barterpost.callback_query(F.data == "confirm_post2")
async def confirm_post(callback: types.CallbackQuery, state: FSMContext):
    """Проверка поста."""
    await callback.answer()
    data = await state.get_data()
    photos = data.get("photos", [])
    if not photos:
        await callback.message.answer("Сначала добавьте хотя бы одно фото.")
        return
    text = (
        f'***_{escape_md(data["title"])}_*** \n\n'
        f'Готовы работать с блогерами по бартеру {escape_md(data["money"])}\\, отправляйте данные на свой блог и статистику\\! \n\n'
        f"❗️***ВАЖНО\\:***\n\n"
        f"***_▫️ Соц\\. сеть\\. Охват и аудитория\\:_***\n"
        f'\\-{escape_md(data["web"])}\n\n'
        f"***_▫️ Что нужно сделать\\?_***\n"
        f'\\-{escape_md(data["descriptions"])}\n\n\n'
        f'🖊️ ***Для сотрудничества отправляйте отклик*** _{escape_md(data["seller"])}_'
    )
    preview_buttons = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="📤 Отправить на модерацию",
                    callback_data="send_to_mod",
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="🔄 Начать заново", callback_data="restart_post"
                )
            ],
        ]
    )
    media_group = [types.InputMediaPhoto(media=file_id) for file_id in photos]
    await callback.message.delete()
    await callback.bot.send_media_group(
        callback.from_user.id, media=media_group
    )
    await callback.bot.send_message(
        callback.from_user.id, text="Проверьте ваш пост"
    )
    await callback.bot.send_message(
        callback.from_user.id,
        text=text,
        reply_markup=preview_buttons,
        parse_mode="MarkdownV2",
    )


@barterpost.callback_query(F.data == "send_to_mod")
async def handle_finish2(callback: types.CallbackQuery, state: FSMContext):
    """Отправка поста на модерацию админу."""
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    data = await state.get_data()
    photos = data.get("photos", [])
    if not photos:
        await callback.message.answer("Сначала добавьте хотя бы одно фото.")
        return
    text = (
        f'***_{escape_md(data["title"])}_*** \n\n'
        f'Готовы работать с блогерами по бартеру {escape_md(data["money"])}\\, отправляйте данные на свой блог и статистику\\! \n\n'
        f"❗️***ВАЖНО\\:***\n\n"
        f"***_▫️ Соц\\. сеть\\. Охват и аудитория\\:_***\n"
        f'\\-{escape_md(data["web"])}\n\n'
        f"***_▫️ Что нужно сделать\\?_***\n"
        f'\\-{escape_md(data["descriptions"])}\n\n\n'
        f'🖊️ ***Для сотрудничества отправляйте отклик*** _{escape_md(data["seller"])}_'
    )
    user_id = callback.from_user.id
    async with async_session() as session:
        chat_user = await session.execute(
            select(ChatPrivatUser).where(ChatPrivatUser.user_id == user_id)
        )
        chat_user = chat_user.scalar()
        thread_id = chat_user.thread_id
    media_group = [types.InputMediaPhoto(media=file_id) for file_id in photos]
    await callback.bot.send_media_group(
        chat_id=KANAL, media=media_group, message_thread_id=thread_id
    )
    buttons = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="✅ Пост принят", callback_data=f"approve_{user_id}"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="❌ Пост отклонён", callback_data=f"reject_{user_id}"
                )
            ],
        ]
    )
    await callback.bot.send_message(
        chat_id=KANAL,
        text=text,
        message_thread_id=thread_id,
        reply_markup=buttons,
        parse_mode="MarkdownV2",
    )
    await state.clear()
    await callback.message.answer(
        "✅ Пост отправлен на модерацию.",
        reply_markup=user_kb(callback.from_user.id),
    )


@barterpost.callback_query(F.data == "restart_post")
async def restart_post(callback: types.CallbackQuery, state: FSMContext):
    """Начать заполнять пост заново."""
    await callback.answer("Начинаем заново.")
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.set_state(PostBarter.title)
    await callback.message.answer(
        "Введите название товара", reply_markup=home()
    )


@barterpost.callback_query(F.data.startswith("approve_"))
async def approve_post2(callback: types.CallbackQuery):
    """Подтвердление от администратора."""
    if callback.from_user.id not in ADMIN_IDS:
        return
    user_id = int(callback.data.split("_")[1])
    try:
        await callback.bot.send_message(
            chat_id=user_id,
            text="✅ Ваш пост принят! Ожидайте размещения. Если остались вопросы можете задать их здесь.",
        )
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception as e:
        await callback.answer("Не удалось отправить сообщение пользователю.")


@barterpost.callback_query(F.data.startswith("reject_"))
async def reject_post2(callback: types.CallbackQuery):
    """Отклонение от администратора."""
    if callback.from_user.id not in ADMIN_IDS:
        return
    user_id = int(callback.data.split("_")[1])
    try:
        await callback.bot.send_message(
            chat_id=user_id,
            text="❌ Ваш пост был отклонен. Попробуйте подать его заново или напишите администратору.",
        )
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.answer(
            "Пользователю отправлено сообщение об отклонении."
        )
    except Exception as e:
        await callback.answer("Не удалось отправить сообщение пользователю.")
