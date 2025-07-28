from datetime import datetime

from sqlalchemy import (BigInteger, Column, DateTime, ForeignKey, Integer,
                        String, Text)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from core.database import Base


class User(Base):
    """Пользователь."""

    telegram_id = Column(BigInteger, unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    username = Column(String(100), nullable=True)
    date_create = Column(DateTime, default=datetime.now)
    post_count = Column(Integer, default=0)
    posts = relationship("Posts", back_populates="user")


class Posts(Base):
    """Пост."""

    date_create = Column(DateTime, default=datetime.now)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    username = Column(String(100), nullable=False)
    post_type = Column(String(20), nullable=False)
    role = Column(String(100), nullable=False)
    contact = Column(String(100), nullable=False)
    about = Column(Text, nullable=False)
    services = Column(Text, nullable=True)
    cases = Column(Text, nullable=True)
    position = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    photos = Column(ARRAY(String), default=list)
    user = relationship("User", back_populates="posts")


class ChatPrivatUser(Base):
    """Чат."""

    user_id = Column(
        BigInteger, ForeignKey("users.telegram_id"), nullable=False
    )
    thread_id = Column(BigInteger, nullable=False)
