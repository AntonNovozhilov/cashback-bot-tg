from sqlalchemy import BigInteger, Integer, String, Boolean, Text, Column, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base
from typing import Optional
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    username = Column(String(100), nullable=True)
    date_create = Column(DateTime, default=datetime.now)
    post_count = Column(Integer, default=0)  
    posts = relationship('Posts', back_populates='user')


class Posts(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    date_create = Column(DateTime, default=datetime.now)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    username = Column(String(100), nullable=False)  # @username для связи
    post_type = Column(String(20), nullable=False)  # "resume" или "vacancy"
    role = Column(String(100), nullable=False)      # кого ищем / кто ты
    contact = Column(String(100), nullable=False)   # @username
    about = Column(Text, nullable=False)            # "о себе" или "о компании"

    # Только для резюме
    services = Column(Text, nullable=True)
    cases = Column(Text, nullable=True)

    # Только для вакансии
    position = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    photos = Column(ARRAY(String), default=list)    # список photo_id

    user = relationship('User', back_populates='posts')


class ChatPrivatUser(Base):
    """Модель чата."""

    __tablename__ = 'chatusers'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.telegram_id'), nullable=False)
    thread_id = Column(BigInteger, nullable=False)
