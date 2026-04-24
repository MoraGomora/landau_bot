from datetime import datetime, timezone

from pydantic import BaseModel, Field

from .mongo import BaseMongoModel
from .types import PyObjectId


class ChatOwner(BaseMongoModel):
    id: PyObjectId = Field(..., alias="_id")
    owner_id: int
    chat_ids: list[int]
    new_chat_id: int
    created_at: datetime
    updated_at: datetime


class CreateChatOwner(BaseModel):
    owner_id: int
    chat_ids: list[int]
    new_chat_id: int | list[int]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))