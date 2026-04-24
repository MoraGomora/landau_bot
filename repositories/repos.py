from .mongo import BaseRepository
from models import Settings, User, ChatUser, ChatOwner


class SettingsRepository(BaseRepository[Settings]):

    def __init__(self, collection) -> None:
        super().__init__(collection, Settings)


class UserRepository(BaseRepository[User]):
    
    def __init__(self, collection) -> None:
        super().__init__(collection, User)


class ChatUserRepository(BaseRepository[ChatUser]):
    
    def __init__(self, collection) -> None:
        super().__init__(collection, ChatUser)


class ChatOwnerRepository(BaseRepository[ChatOwner]):
    
    def __init__(self, collection) -> None:
        super().__init__(collection, ChatOwner)