from enum import StrEnum


class Permission(StrEnum):
    USER = "user"
    VIP = "vip"
    MODERATOR = "moderator"
    OWNER = "owner"