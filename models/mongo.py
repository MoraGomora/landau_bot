from typing import Any

from pydantic import BaseModel, field_serializer


class BaseMongoModel(BaseModel):

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

    @field_serializer("*", when_used="unless-none")
    def serialize_all(self, value) -> str | Any:
        from datetime import datetime

        if isinstance(value, datetime):
            return value.isoformat()

        return value