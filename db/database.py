from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os

from config import config



engine = create_async_engine(
    f'postgresql+asyncpg://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}@postgres-bot2:5432/{config.POSTGRES_DATABASE}',
    echo=False
)

async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)