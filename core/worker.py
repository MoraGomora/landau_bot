import asyncio
from typing import Callable, Awaitable, NoReturn


class SimpleWorker:

    def __init__(
            self,
            name: str,
            func: Callable[[], Awaitable[None]],
            interval: int,
            lock: asyncio.Lock | None = None
    ) -> None:
        self._name = name
        self._func = func
        self._interval = interval
        self._task: asyncio.Task | None = None
        self._lock = lock or asyncio.Lock()

    async def _run(self) -> NoReturn:
        while True:
            try:
                if self._lock.locked():
                    await asyncio.sleep(self._interval)
                    continue

                async with self._lock:
                    await self._func()
            except Exception as e:
                raise e
            
            await asyncio.sleep(self._interval)

    def start(self) -> asyncio.Task:
        self._task = asyncio.create_task(self._run(), name=self._name)
        return self._task

    def stop(self) -> bool | None:
        if self._task:
            return self._task.cancel()