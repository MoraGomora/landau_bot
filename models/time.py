from pydantic import BaseModel


class BanTime(BaseModel):
    hours: int = 0
    minutes: int = 0
    seconds: int = 0