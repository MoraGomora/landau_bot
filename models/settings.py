from datetime import datetime, timezone

from pydantic import Field

from .mongo import BaseMongoModel
from .types import PyObjectId


class Settings(BaseMongoModel):
    id: PyObjectId = Field(..., alias="_id")
    chat_id: int
    chat_name: str
    owner_id: int
    has_send_violation_msg: bool
    has_dynamic_violation_time: bool
    has_chat_dialog: bool
    created_at: datetime
    updated_at: datetime


class CreateSettings(BaseMongoModel):
    chat_id: int
    chat_name: str
    owner_id: int
    has_send_violation_msg: bool
    has_dynamic_violation_time: bool
    has_chat_dialog: bool
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))