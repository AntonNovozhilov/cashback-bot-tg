from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import KANAL
from core.database import async_session
from fsm.states import Registration
from keyboards.kb_user import user_kb
from models.models import User
from utils.chat import caht_add

from .funcs import get_user_from_db

router_start = Router()


@router_start.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    telegram_id = message.from_user.id

    async with async_session() as session:
        user = await get_user_from_db(session=session, telegram_id=telegram_id)
        if user:
            await message.answer(
                f"Привет, {user.name}!",
                reply_markup=user_kb(message.from_user.id),
            )
        else:
            await message.answer("Добро пожаловать! Введи своё имя:")
            await state.set_state(Registration.name)


@router_start.message(Registration.name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()
    telegram_id = message.from_user.id
    real_username = message.from_user.username

    async with async_session() as session:
        user = User(telegram_id=telegram_id, name=name, username=real_username)
        session.add(user)
        await session.commit()
        try:
            new_topic = await message.bot.create_forum_topic(
                chat_id=KANAL, name=f"{real_username} \ {telegram_id}"
            )
            thread_id = new_topic.message_thread_id

            await caht_add(user.telegram_id, thread_id)

            await message.bot.send_message(
                chat_id=KANAL,
                message_thread_id=thread_id,
                text=f"🟢 Новый пользователь зарегистрировался!\n\n<b>{name}</b>",
            )
        except TelegramAPIError as e:
            await message.answer(
                "✅ Вы зарегистрированы, но произошла ошибка при создании темы."
            )

    await message.answer(
        f"✅ Добро пожаловать, {name}!",
        reply_markup=user_kb(message.from_user.id),
    )
    await state.clear()
