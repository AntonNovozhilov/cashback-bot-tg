import asyncio
from collections import defaultdict
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from fsm.states import Post
from keyboards.inline import (
    type_keyboard, contact_keyboard, cancel_keyboard,
    skip_photo_keyboard, confirm_keyboard, moderation_keyboard
)
from keyboards.inline_kb import finish_kb3
from db.database import async_session
from db.models import ChatPrivatUser, User, Posts
from utils.post_builder import build_post_text
from config import KANAL
from sqlalchemy import select
from .funcs import get_user_from_db

router = Router()
media_group_buffer = defaultdict(list)


# === Шаг 1 ===

@router.callback_query(F.data == 'create_offer')
async def start_post_creation(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer("Шаг 1/6. Что вы хотите разместить?", reply_markup=type_keyboard())
    await state.set_state(Post.post_type)


# === Шаг 2 ===

@router.callback_query(F.data.startswith("type_"))
async def process_post_type(callback: CallbackQuery, state: FSMContext):
    post_type = callback.data.split("_")[1]
    await state.update_data(post_type=post_type)

    question = "Кто вы?" if post_type == "resume" else "Кого вы ищете?"
    await callback.message.answer(f"Шаг 2/6. {question}", reply_markup=cancel_keyboard)
    await state.set_state(Post.role)
    await callback.answer()


@router.message(Post.role)
async def process_role(message: Message, state: FSMContext):
    await state.update_data(role=message.text)
    await message.answer("Шаг 3/6. Укажите контакт для связи", reply_markup=contact_keyboard())
    await state.set_state(Post.contact_choice)


# === Шаг 3: Контакт ===

@router.callback_query(F.data == "contact_self")
async def process_contact_self(callback: CallbackQuery, state: FSMContext):
    async with async_session() as session:
        user = await get_user_from_db(session, callback.from_user.id)

    if not user.username:
        await callback.message.answer("❗ У вас не установлен username. Введите контакт вручную:", reply_markup=cancel_keyboard)
        await state.set_state(Post.contact_custom)
    else:
        await state.update_data(contact="@" + user.username)
        await ask_about_section(callback, state)


@router.callback_query(F.data == "contact_custom")
async def process_contact_custom(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите контакт вручную (например: @username):", reply_markup=cancel_keyboard)
    await state.set_state(Post.contact_custom)


@router.message(Post.contact_custom)
async def save_custom_contact(message: Message, state: FSMContext):
    contact = message.text.strip()
    if not contact.startswith("@"):
        await message.answer("❗ Контакт должен начинаться с '@'")
        return
    await state.update_data(contact=contact)
    await ask_about_section(message, state)


# === Шаг 4: Описание ===

async def ask_about_section(event, state: FSMContext):
    data = await state.get_data()
    post_type = data.get("post_type")

    text = (
        "Шаг 4.1/6. Напишите о себе:"
        if post_type == "resume"
        else "Шаг 4.1/6. Расскажите о себе как о работодателе:"
    )

    if isinstance(event, CallbackQuery):
        await event.message.answer(text, reply_markup=cancel_keyboard)
    elif isinstance(event, Message):
        await event.answer(text, reply_markup=cancel_keyboard)

    if post_type == "resume":
        await state.set_state(Post.about_you)
    else:
        await state.set_state(Post.about_company)


@router.message(Post.about_you)
async def process_about_you(message: Message, state: FSMContext):
    await state.update_data(about_you=message.text)
    await message.answer("Шаг 4.2/6. Опишите свои услуги:", reply_markup=cancel_keyboard)
    await state.set_state(Post.services)


@router.message(Post.services)
async def process_services(message: Message, state: FSMContext):
    await state.update_data(services=message.text)
    await message.answer("Шаг 4.3/6. Преимущества или кейсы:", reply_markup=cancel_keyboard)
    await state.set_state(Post.cases)


@router.message(Post.about_company)
async def process_about_company(message: Message, state: FSMContext):
    await state.update_data(about_company=message.text)
    await message.answer("Шаг 4.2/6. Опишите должность:", reply_markup=cancel_keyboard)
    await state.set_state(Post.position)


@router.message(Post.position)
async def process_position(message: Message, state: FSMContext):
    await state.update_data(position=message.text)
    await message.answer("Шаг 4.3/6. Требования:", reply_markup=cancel_keyboard)
    await state.set_state(Post.requirements)


# === Шаг 5: Фото ===

@router.message(Post.cases)
@router.message(Post.requirements)
async def move_to_photo_step(message: Message, state: FSMContext):
    if message.text:
        key = "cases" if await state.get_state() == Post.cases else "requirements"
        await state.update_data({key: message.text})
    await message.answer("Шаг 5/6. Прикрепите фото (или нажмите 'Пропустить')", reply_markup=skip_photo_keyboard)
    await state.set_state(Post.photo)


@router.message(Post.photo, ~F.photo)
async def invalid_photo_input(message: Message):
    await message.answer("❗ Прикрепите *фотографию* через 📎 > Фото.")


@router.message(Post.photo, F.photo)
async def save_photo(message: Message, state: FSMContext):
    if message.media_group_id:
        media_group_buffer[message.media_group_id].append(message.photo[-1].file_id)
        if len(media_group_buffer[message.media_group_id]) == 1:
            await asyncio.sleep(1.5)
            photo_ids = media_group_buffer.pop(message.media_group_id)
            await state.update_data(photos=photo_ids)
            await message.answer("🖼 Фото добавлены. Нажмите кнопку ниже, чтобы завершить.", reply_markup=finish_kb3())
    else:
        data = await state.get_data()
        photos = data.get('photos', [])
        photos.append(message.photo[-1].file_id)
        await state.update_data(photos=photos)
        await message.answer("🖼 Фото добавлены. Нажмите кнопку ниже, чтобы завершить.", reply_markup=finish_kb3())


@router.callback_query(F.data == "skip_photo")
async def skip_photo(callback: CallbackQuery, state: FSMContext):
    await state.update_data(photos=[])
    await confirm_post(callback, state)


# === Шаг 6: Подтверждение ===

@router.callback_query(F.data == "finish_post3")
async def confirm_post(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    async with async_session() as session:
        user = await get_user_from_db(session, callback.from_user.id)

        post = Posts(
            user_id=user.id,
            username=user.username,
            post_type=data["post_type"],
            role=data["role"],
            contact=data["contact"],
            about=data.get("about_you") or data.get("about_company"),
            services=data.get("services"),
            cases=data.get("cases"),
            position=data.get("position"),
            requirements=data.get("requirements"),
            photos=data.get("photos", []),
        )
        session.add(post)
        user.post_count = (user.post_count or 0) + 1
        await session.commit()

    post_text = build_post_text(user.name, data)
    photos = data.get("photos", [])

    if photos:
        media_group = [InputMediaPhoto(media=file_id) for file_id in photos]
        await callback.bot.send_media_group(callback.from_user.id, media_group)
        await asyncio.sleep(1.5)
        await callback.bot.send_message(callback.from_user.id, post_text, reply_markup=confirm_keyboard(), parse_mode="HTML")
        await state.set_state(Post.confirm)
    else:
        await callback.bot.send_message(callback.from_user.id, post_text, reply_markup=confirm_keyboard(), parse_mode="HTML")
        await state.set_state(Post.confirm)


@router.callback_query(F.data == "confirm_ok", Post.confirm)
async def confirm_send(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    async with async_session() as session:
        user = await get_user_from_db(session, callback.from_user.id)
        result = await session.execute(select(ChatPrivatUser).where(ChatPrivatUser.user_id == callback.from_user.id))
        chat_user = result.scalar()
    post_text = build_post_text(user.name, data)
    photos = data.get('photos', [])
    if photos:
        media_group = [InputMediaPhoto(media=file_id) for file_id in photos]
        await callback.bot.send_media_group(chat_id=KANAL, media=media_group, message_thread_id=chat_user.thread_id)
        await asyncio.sleep(1.5)
    await callback.bot.send_message(
        KANAL,
        post_text,
        message_thread_id=chat_user.thread_id,
        reply_markup=moderation_keyboard(user.telegram_id),
        parse_mode="HTML"
    )
    await callback.message.answer("✅ Пост отправлен на модерацию!")
    await state.clear()


@router.callback_query(F.data == "confirm_restart", Post.confirm)
async def confirm_restart(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("⛔️ Вы отменили создание поста.")
    await state.clear()
