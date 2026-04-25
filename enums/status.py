from enum import StrEnum


class Status(StrEnum):
    NONE = "none"
    PENDING = "pending"
    PROCESSING = "processing"
    COUNTING = "counting"
    DONE = "done"
    FAILED = "failed"