from pydantic import BaseModel, Field
from typing import Any
import uuid

class Message(BaseModel):
    id: int = Field(..., description="Идентификатор сообщения")
    chat_id: int = Field(..., description="Идентификатор чата")
    sender_id: int = Field(..., description="Идентификатор отправителя")
    text: str | None = Field(..., description="Текст сообщения")
    sended_at: str = Field(..., description="Дата отправки сообщения")
    attachments: dict


class Event(BaseModel):
    name:str
    data:Any
    id: uuid.UUID
