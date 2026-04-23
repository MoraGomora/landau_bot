from pydantic import BaseModel


class Violation(BaseModel):
    duration: int
    until: int