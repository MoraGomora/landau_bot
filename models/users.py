from datetime import datetime, timezone

from pydantic import BaseModel, Field

from .mongo import BaseMongoModel
from .types import PyObjectId
from enums import Status


class User(BaseMongoModel):
    id: PyObjectId = Field(..., alias="_id")
    user_id: int
    has_private: bool
    permission: str
    created_at: datetime
    updated_at: datetime


class ChatUser(BaseMongoModel):
    id: PyObjectId = Field(..., alias="_id")
    user_id: int
    chat_id: int
    join_attempts: int
    status: Status
    created_at: datetime
    updated_at: datetime


class CreateUser(BaseModel):
    user_id: int
    has_private: bool = False
    permission: str = "user"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CreateChatUser(BaseModel):
    user_id: int
    chat_id: int
    join_attempts: int = 0
    status: Status = Status.NONE
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))