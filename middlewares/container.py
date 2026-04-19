from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable

from core.container.app import AppContainer


class ContainerMiddleware(BaseMiddleware):
    def __init__(self, container: AppContainer):
        self.container = container

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any],
    ):
        data["container"] = self.container
        return await handler(event, data)