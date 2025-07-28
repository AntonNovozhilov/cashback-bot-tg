from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, select

from core.database import async_session
from models.models import ChatPrivatUser, User


async def get_user_from_db(session, telegram_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        result = result.scalar()
        return result


async def add_user(tg_id, username=None, first_name=None, last_name=None):
    """Добавление пользователя."""
    async with async_session() as session:
        user = await session.scalar(
            select(User).where(User.telegram_id == tg_id)
        )
        if not user:
            session.add(User(telegram_id=tg_id, username=username))
            await session.commit()


async def caht_add(tg_id, thread_id):
    """Добавление чата в базу."""
    async with async_session() as session:
        chat_user = await session.scalar(
            select(ChatPrivatUser).where(ChatPrivatUser.user_id == tg_id)
        )
        if not chat_user:
            session.add(ChatPrivatUser(user_id=tg_id, thread_id=thread_id))
            await session.commit()


async def chat_privat(tg_id):
    """Список чатов."""
    async with async_session() as session:
        result = await session.scalars(
            select(ChatPrivatUser.user_id).where(
                ChatPrivatUser.user_id == tg_id
            )
        )
        return result.all()
