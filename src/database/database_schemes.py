from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Boolean, CheckConstraint


from typing import Annotated

from .database_engine import get_session

str_256 = Annotated[str, 256]


class Base(DeclarativeBase):
    type_annotation_map = {
        str_256: String(256)
    }


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] 
    name: Mapped[str_256]
    vk_id: Mapped[int]


class MessageTranslate(Base):
    __tablename__ = "message_translate"

    mh_message_id: Mapped[int] =  mapped_column()
    vk_chat_id: Mapped[int] = mapped_column(primary_key=True)
    vk_message_id: Mapped[int] = mapped_column(primary_key=True)
