from aiogram import F, Router, types
from sqlalchemy import select
from db.models import ChatPrivatUser
from db.database import async_session
from utils.chat import add_user, caht_add, chat_privat, get_user_from_db
from config import KANAL

private = Router()

@private.message(F.chat.type == 'private')
async def private_chat_message(message: types.Message):
    '''Обработка всех сообщений и инициализация теммы в группе.'''
    user_id = message.from_user.id
    username = message.from_user.username
    async with async_session() as session:
        user = await get_user_from_db(session, user_id)

    if not user:
        await message.answer("❗ Сначала зарегистрируйтесь через команду /start.")
        return  # ⛔ Не продолжаем

    # await add_user(user_id, username=username)
    chat = await chat_privat(user_id)
    if user_id not in chat:
        topic_title = f'{username}'
        new_topic = await message.bot.create_forum_topic(chat_id=KANAL, name=topic_title)
        thread_id = new_topic.message_thread_id
        await caht_add(tg_id=user_id, thread_id=thread_id)
        await message.bot.send_message(chat_id=KANAL, text='Клиент пишет', message_thread_id=thread_id)
    else:
        async with async_session() as session:
            chat_user = await session.execute(select(ChatPrivatUser).where(ChatPrivatUser.user_id == user_id))
            chat_user = chat_user.scalar()
            thread_id = chat_user.thread_id if chat_user else None
    if thread_id:
        await message.bot.forward_message(
            chat_id=KANAL,
            from_chat_id=message.chat.id,
            message_id=message.message_id,
            message_thread_id=thread_id
        )

@private.message(F.chat.id == KANAL, F.message_thread_id)
async def from_admin_to_user(message: types.Message):
    '''Ответ клиенту через бота и тему.'''
    thread_id = message.message_thread_id
    async with async_session() as session:
        chat_user = await session.execute(select(ChatPrivatUser).where(ChatPrivatUser.thread_id == thread_id))
        chat_user = chat_user.scalar()
        if chat_user:
            try:
                await message.bot.copy_message(
                    chat_id=chat_user.user_id,
                    from_chat_id=message.chat.id,
                    message_id=message.message_id
                )
            except Exception as e:
                await message.reply(f'Не удалось переслать сообщение: {e}')
