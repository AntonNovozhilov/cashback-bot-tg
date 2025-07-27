from aiogram import Router, F
from aiogram.types import CallbackQuery
from db.database import async_session
from db.models import User, Posts
from keyboards.inline import channel_post_keyboard
from utils.post_builder import build_post_text
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from config import config  # config.admin_ids
from keyboards.admin import admin_panel_keyboard

import os
from utils.export import export_to_excel  # экспорт из прошлого шага
from aiogram.types import FSInputFile

router = Router()

CHANNEL_ID = -1002884308237  # Заменить на ID твоего канала


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id in config.admin_ids:
        await message.answer("Админ-панель:", reply_markup=admin_panel_keyboard())
    else:
        await message.answer("Доступ запрещён.")

@router.callback_query(F.data.startswith("moderate_accept_"))
async def accept_post(callback: CallbackQuery):
    user_telegram_id = int(callback.data.split("_")[-1])

    async with async_session() as session:
        # Поиск пользователя по telegram_id
        user = await session.scalar(
            select(User)
            .where(User.telegram_id == user_telegram_id)
            .options(selectinload(User.posts))
        )


        if not user or not user.posts:
            await callback.answer("Пост не найден", show_alert=True)
            return

        last_post = await session.scalar(
            select(Posts).where(Posts.user_id == user.id).order_by(Posts.date_create.desc())
        )
        post_text = build_post({
            "role": last_post.role,
            "name": user.name,
            "username": last_post.username,
            "marketplace": last_post.marketplace,
            "category": last_post.category,
            "achievements": last_post.achievements,
            "about": last_post.about,
            "expectations": last_post.expectations,
            "extra": last_post.extra,
        })



        # Отправляем пост в канал
        await callback.bot.send_message(
            chat_id=CHANNEL_ID,
            text=post_text,
            reply_markup=channel_post_keyboard(user.username)
        )

        # Уведомляем пользователя
        await callback.bot.send_message(
            chat_id=user.telegram_id,
            text="✅ Ваш пост был одобрен и размещён в канале!"
        )

        # Удаляем inline-кнопки у админа
        await callback.message.edit_reply_markup()
        await callback.answer("Пост размещён ✅")



@router.callback_query(F.data.startswith("moderate_reject_"))
async def reject_post(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[-1])
    await callback.bot.send_message(user_id, "❌ К сожалению, ваш пост не был одобрен.")

    await callback.message.edit_reply_markup()
    await callback.answer("Пользователь уведомлён ❌")

@router.callback_query(F.data == "download_excel")
async def handle_download_excel(callback: CallbackQuery):
    if callback.from_user.id not in config.admin_ids:
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    await callback.answer("📦 Готовим файл...")
    await export_to_excel()
    file = FSInputFile("export.xlsx")
    await callback.message.answer_document(file, caption="Вот база данных 📊")
