from enum import StrEnum


class Status(StrEnum):
    NONE = "none"
    PENDING = "pending"
    DONE = "done"
    FAILED = "failed"