from .mongo import BaseRepository
from models import Settings, User, ChatUser


class SettingsRepository(BaseRepository[Settings]):

    def __init__(self, collection) -> None:
        super().__init__(collection, Settings)


class UserRepository(BaseRepository[User]):
    
    def __init__(self, collection) -> None:
        super().__init__(collection, User)


class ChatUserRepository(BaseRepository[ChatUser]):
    
    def __init__(self, collection) -> None:
        super().__init__(collection, ChatUser)