from aiogram.types import Message, CallbackQuery, FSInputFile
from command_text import FAQ, TEXT_REQ
from keyboards.admin import is_admin, kb_admin
from aiogram import Router, F
import os
from dotenv import load_dotenv
from sqlalchemy import select
from db.models import User, ChatPrivatUser
from db.database import async_session
from datetime import datetime, timedelta, timezone
from aiogram.filters import Command
from config import CHANNEL_ID_OFFER, KANAL, PRICE_MESSAGE_ID_OFFER, config
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.inline import confirm_keyboard  # admin_ids список айдишников админов
from config import (
    CHANNEL_ID_BARTER,
    CHANNEL_ID_CASH,
    CHANNEL_INFO_MESSAGE,
    CHAT_ID,
    PRICE_MESSAGE_ID_BARTER,
    PRICE_MESSAGE_ID_CASH,
    count_price_in_admin,
    count_users_in_admin,
    home,
    kb_admin_pannel_text,
    kb_admin_text,
    kb_cannals_text,
    kb_create_post_text,
    kb_faq_text,
    kb_price_text,
    kb_requis_text,
)
from keyboards.inline_kb import inline_create_post, inline_price
from keyboards.kb_user import user_kb
from keyboards.admin import kb_admin


load_dotenv('.env')

commands = Router()

@commands.message(F.text == 'Админка')
async def panel_admin(message: Message):
    '''Вызов меню админа.'''
    if not is_admin(message.from_user.id):
        return await message.answer("У вас нет доступа к админке.")
    
    await message.answer(
        "Вы вошли в админку", reply_markup=kb_admin(message.from_user.id)
    )

@commands.message(F.text == 'В главное меню')
async def main_menu(message: Message, state: FSMContext):
    '''Обработка нажатия на кнопку главное меню.'''

    await state.clear()
    await message.answer('Вы вернулись в главное меню', reply_markup=user_kb(message.from_user.id))

@commands.message(F.text == kb_create_post_text)
async def inline_create_posts(message: Message):
    """Вызов 2 инлайн книпки при нажатии на меню Составить пост."""
    await message.answer(
        "Выберите в какой канал составить пост", reply_markup=inline_create_post()
    )


@commands.message(F.text == kb_price_text)
async def price(message: Message):
    """Вызов 2 инлайн книпки при нажатии на меню Прайс."""
    await message.answer("Выберите канал 👇", reply_markup=inline_price())


@commands.message(F.text == kb_faq_text)
async def faq(message: Message):
    """Вызов поста с FAQом."""
    photo_path = "images/faq.jpg"
    photo = FSInputFile(photo_path)
    await message.bot.send_photo(
        chat_id=message.chat.id, photo=photo, caption=FAQ, parse_mode="MarkdownV2"
    )

@commands.message(F.text == kb_cannals_text)
async def list_channals(message: Message):
    """Вызов поста с списком каналов."""
    await message.bot.forward_message(
        chat_id=message.chat.id,
        from_chat_id=CHANNEL_ID_BARTER,
        message_id=CHANNEL_INFO_MESSAGE,
    )

@commands.message(F.text == kb_requis_text)
async def reqwuis(message: Message):
    """Вызов поста с реквизитами для оплаты."""
    await message.answer(text=TEXT_REQ)


@commands.message(F.text == kb_admin_text)
async def link_admin(message: Message):
    """Вызов поста с сылкой на админа."""
    await message.answer(
        text="[Администратор Юлия](https://t.me/@Juli_Novozhilova)",
        parse_mode="MarkdownV2",
    )

@commands.message(F.text == kb_admin_pannel_text)
async def panel_admin(message: Message):
    """Вызов меню админа."""
    await message.answer(
        "Вы вошли в админку", reply_markup=kb_admin(message.from_user.id)
    )


@commands.message(F.text == home)
async def panel_admin_out(message: Message):
    """Выйти из меню админа."""
    await message.answer(
        "Вы вышли из меню админа", reply_markup=user_kb(message.from_user.id)
    )

@commands.callback_query(F.data == "price_cash")
async def price_cashback(callback: CallbackQuery):
    """При нажатии на кнопку 1 пересылает сообщение из канала с прайсом кешбека."""
    # await price_cashback_add(callback.from_user.id)
    await callback.message.bot.forward_message(
        chat_id=callback.message.chat.id,
        from_chat_id=CHANNEL_ID_CASH,
        message_id=PRICE_MESSAGE_ID_CASH,
    )
    user_id = callback.from_user.id
    async with async_session() as session:
        chat_user = await session.execute(select(ChatPrivatUser).where(ChatPrivatUser.user_id == user_id))
        chat_user = chat_user.scalar()
    await callback.message.bot.send_message(
        chat_id=KANAL,
        message_thread_id=chat_user.thread_id,
        text=f"Пользователь {callback.from_user.first_name} запросил прайс по кешбеку"
    )


@commands.callback_query(F.data == "price_barter")
async def price_barter(callback: CallbackQuery):
    """При нажатии на кнопку 2 пересылает сообщение из канала с прайсом бартера."""
    # await price_barter_add(callback.from_user.id)
    await callback.message.bot.forward_message(
        chat_id=callback.message.chat.id,
        from_chat_id=CHANNEL_ID_BARTER,
        message_id=PRICE_MESSAGE_ID_BARTER,
    )
    user_id = callback.from_user.id
    async with async_session() as session:
        chat_user = await session.execute(select(ChatPrivatUser).where(ChatPrivatUser.user_id == user_id))
        chat_user = chat_user.scalar()
    await callback.message.bot.send_message(
        chat_id=KANAL,
        message_thread_id=chat_user.thread_id,
        text=f"Пользователь {callback.from_user.first_name} запросил прайс по бартеру"
    )

@commands.callback_query(F.data == "price_offer")
async def price_offer(callback: CallbackQuery):
    """При нажатии на кнопку 'price_offer' отправляет текст из файла price.txt."""
    await callback.message.bot.forward_message(
        chat_id=callback.message.chat.id,
        from_chat_id=CHANNEL_ID_OFFER,
        message_id=PRICE_MESSAGE_ID_OFFER,
    )
    user_id = callback.from_user.id
    async with async_session() as session:
        chat_user = await session.execute(select(ChatPrivatUser).where(ChatPrivatUser.user_id == user_id))
        chat_user = chat_user.scalar()
    await callback.message.bot.send_message(
        chat_id=KANAL,
        message_thread_id=chat_user.thread_id,
        text=f"Пользователь {callback.from_user.first_name} запросил прайс по вакансиям"
    )

@commands.message(F.chat.id == KANAL, F.message_thread_id, Command("pc"))
async def from_admin_to_user_cashbak(message: Message):
    """Администратор может отправить прайс кешбека пользователю командой."""
    thread_id = message.message_thread_id
    async with async_session() as session:
        chat_user = await session.scalar(
            select(ChatPrivatUser).where(ChatPrivatUser.thread_id == thread_id)
        )
        if chat_user:
            await message.bot.forward_message(
                chat_id=chat_user.user_id,
                from_chat_id=CHANNEL_ID_CASH,
                message_id=PRICE_MESSAGE_ID_CASH,
            )
            await message.answer('Сообщение с прайсом по кешбеку ушло')


@commands.message(F.chat.id == KANAL, F.message_thread_id, Command("pb"))
async def from_admin_to_user_barter(message: Message):
    """Администратор может отправить прайс бартера пользователю командой."""
    thread_id = message.message_thread_id
    async with async_session() as session:
        chat_user = await session.scalar(
            select(ChatPrivatUser).where(ChatPrivatUser.thread_id == thread_id)
        )
        if chat_user:
            await message.bot.forward_message(
                chat_id=chat_user.user_id,
                from_chat_id=CHANNEL_ID_BARTER,
                message_id=PRICE_MESSAGE_ID_BARTER,
            )
            await message.answer('Сообщение с прайсом по бартеру ушло')

@commands.message(F.chat.id == KANAL, F.message_thread_id, Command("po"))
async def from_admin_to_user_offer(message: Message):
    """Администратор может отправить прайс бартера пользователю командой."""
    thread_id = message.message_thread_id
    async with async_session() as session:
        chat_user = await session.scalar(
            select(ChatPrivatUser).where(ChatPrivatUser.thread_id == thread_id)
        )
        if chat_user:
            await message.bot.forward_message(
                chat_id=chat_user.user_id,
                from_chat_id=CHANNEL_ID_OFFER,
                message_id=PRICE_MESSAGE_ID_OFFER,
            )
            await message.answer('Сообщение с прайсом по вакансиям ушло')

@commands.message(F.chat.id == KANAL, F.message_thread_id, Command("r"))
async def from_admin_to_user_req(message: Message):
    """Администратор может отправить реквизиты пользователю командой."""
    thread_id = message.message_thread_id
    async with async_session() as session:
        chat_user = await session.scalar(
            select(ChatPrivatUser).where(ChatPrivatUser.thread_id == thread_id)
        )
        if chat_user:
                await message.bot.send_message(chat_id=chat_user.user_id, text=TEXT_REQ)
                await message.answer('Сообщение с реквизитами ушло')


@commands.message(F.text == 'Выйти')
async def panel_admin_out(message: Message):
    """Выйти из меню админа."""
    await message.answer(
        "Вы вышли из меню админа", reply_markup=user_kb(message.from_user.id)
    )

async def count_users():
    '''Подсчет пользователей.'''
    async with async_session() as session:
        return await session.scalars(select(User))
    
async def count_users_today():
    """Пользователи, зарегистрированные сегодня (UTC)."""
    now = datetime.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0).replace(tzinfo=None)
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999).replace(tzinfo=None)

    async with async_session() as session:
        return await session.scalars(
            select(User).where(
                User.date_create >= start_of_day,
                User.date_create <= end_of_day
            )
        )


async def count_users_week():
    """Пользователи за последние 7 дней (UTC)."""
    now = datetime.now()
    week_ago = now - timedelta(days=7)

    async with async_session() as session:
        return await session.scalars(
            select(User).where(User.date_create >= week_ago)
        )

    
@commands.message(F.text == 'Статистика')
async def count_us(message: Message):
    """Команда: показать статистику пользователей."""
    if not is_admin(message.from_user.id):
        return await message.answer("У вас нет доступа.")

    users = await count_users()
    today_users = await count_users_today()
    week_users = await count_users_week()

    count_all = len(list(users))
    count_today = len(list(today_users))
    count_week = len(list(week_users))

    await message.answer(
        f"📊 *Статистика пользователей:*\n\n"
        f"👥 Всего: {count_all}\n"
        f"📅 Сегодня: {count_today}\n"
        f"📈 За 7 дней: {count_week}",
        parse_mode="Markdown"
    )

class Edit(StatesGroup):
    waiting_price = State()
    confirm_price = State()



@commands.message(Command("editprice"))
async def edit_price_command(message: Message, state: FSMContext):
    if message.from_user.id not in config.admin_ids:
        await message.answer("⛔ У вас нет доступа к этой команде.")
        return

    await message.answer("✏️ Введите новый текст для /price:")
    await state.set_state(Edit.waiting_price)


@commands.message(Edit.waiting_price)
async def preview_price_text(message: Message, state: FSMContext):
    new_text = message.text.strip()
    await state.update_data(price_text=new_text)

    await message.answer(
        f"Вот как будет выглядеть новый текст:\n\n{new_text}",
        reply_markup=confirm_keyboard()
    )
    await state.set_state(Edit.confirm_price)


@commands.callback_query(F.data == "confirm_ok", Edit.confirm_price)
async def confirm_price(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    new_text = data.get("price_text", "")

    with open("price.txt", "w", encoding="utf-8") as f:
        f.write(new_text)

    await callback.message.edit_text("✅ Текст успешно обновлён.")
    await state.clear()
    await callback.answer()


@commands.callback_query(F.data == "confirm_restart", Edit.confirm_price)
async def cancel_price(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Изменение отменено.")
    await state.clear()
    await callback.answer()