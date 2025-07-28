import pandas as pd
from aiogram import F, Router
from aiogram.types import FSInputFile, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config import config
from models.models import Posts, User

base = Router()


@base.message(F.text == "Скачать базу")
async def export_to_excel(message: Message):
    engine = create_async_engine(
        f"postgresql+asyncpg://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}@postgres-bot2:5432/{config.POSTGRES_DATABASE}"
    )
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        result_users = await session.execute(select(User))
        users = result_users.scalars().all()

        users_data = [
            {
                "ID": u.id,
                "Имя": u.name,
                "Username": u.username,
                "Telegram ID": u.telegram_id,
                "Дата регистрации": u.date_create.strftime("%Y-%m-%d %H:%M"),
                "Постов": u.post_count,
            }
            for u in users
        ]

        df_users = pd.DataFrame(users_data)
        result_posts = await session.execute(select(Posts))
        posts = result_posts.scalars().all()

        posts_data = [
            {
                "ID": p.id,
                "User ID": p.user_id,
                "Ник": p.username,
                "Дата поста": p.date_create.strftime("%Y-%m-%d %H:%M"),
            }
            for p in posts
        ]

        df_posts = pd.DataFrame(posts_data)
        filepath = "export.xlsx"
        with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
            df_users.to_excel(writer, sheet_name="Users", index=False)
            df_posts.to_excel(writer, sheet_name="Posts", index=False)
    file = FSInputFile(filepath)
    await message.answer_document(file, caption="📦 Экспорт базы данных")
