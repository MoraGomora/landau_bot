import asyncio
from typing import Dict, Callable

from structlog.typing import FilteringBoundLogger

from .worker import SimpleWorker


class SimpleWorkerManager:

    def __init__(self, logger: FilteringBoundLogger) -> None:
        self._workers: Dict[str, SimpleWorker] = {}
        self._logger = logger

    def register(self, worker: SimpleWorker) -> None:
        if worker._name in self._workers:
            available = self._workers[worker._name]

            self._logger.error(
                "Worker was registered",
                worker_name=available._name,
                worker_func=available._func,
                worker_interval=available._interval
            )

            raise ValueError(f"Worker {available._name} was registered")
        
        self._workers[worker._name] = worker
        self._logger.debug(
            "Worker registered",
            worker_name=worker._name,
            worker_func=worker._func,
            worker_interval=worker._interval
        )

    def _make_callback(self, name: str) -> Callable[..., None]:
        def _on_done(task: asyncio.Task) -> None:
            if task.cancelled():
                return
            
            exc = task.exception()
            if exc:
                self._logger.error(
                    event="Worker crashed with an exception",
                    worker=name,
                    error=str(exc)
                )
        return _on_done

    def start_all(self) -> None:
        if not self._workers:
            return
        
        for worker in self._workers.values():
            result = worker.start()

            if not result:
                self._logger.error(
                    "Failed to start task",
                    task_name=worker._name
                )

                return
            
            worker._task.add_done_callback(self._make_callback(worker._name))
            self._logger.debug(
                "Task started successfully",
                task_name=worker._name
            )
        
        self._logger.debug(
            "All workers started",
            workers_count=len(self._workers)
        )

    def stop_all(self) -> None:
        if not self._workers:
            return
        
        for worker in self._workers.values():
            result = worker.stop()

            if not result:
                self._logger.error(
                    "Failed to stop task",
                    task_name=worker._name
                )

                return
            
            self._logger.debug(
                "Task stopped successfully",
                task_name=worker._name
            )
        
        self._logger.debug(
            "All workers stopped",
            workers_count=len(self._workers)
        )


class SimpleTaskManager:

    def __init__(self, logger: FilteringBoundLogger) -> None:
        self._tasks: Dict[str, asyncio.Task] = {}
        self.logger = logger

    def shedule(self, name: str, func: Callable, delay: int) -> None:
        async def _run():
            await asyncio.sleep(delay)
            try:
                await func()
            except Exception as e:
                self.logger.error(
                    "Task has an error",
                    task=name,
                    error=str(e)
                )
            finally:
                self.logger.debug(
                    "Task completed. Removing from manager...",
                    task=name
                )

                self._tasks.pop(name, None)

        if name in self._tasks:
            self.logger.debug(
                "Task with this name is already sheduled. Cancelling previous task...",
                name=name
            )
            
            self._tasks.get(name).cancel()
        
        self._tasks[name] = asyncio.create_task(_run(), name=name)

        self.logger.debug(
            "Task created with delay",
            name=name,
            delay=delay
        )

    def cancel(self, name: str) -> None:
        task = self._tasks.pop(name)
        if not task:
            self.logger.error(
                "Task with this name is unavailable",
                name=name
            )

            return
        
        cancelled = task.cancel()
        if not cancelled:
            self.logger.error(
                "Task was not cancelled",
                name=name
            )
            
            return
        
        self.logger.debug(
            "Task cancelled successfully",
            name=name
        )

    def cancel_all(self) -> None:
        for name, task in self._tasks.items():
            cancelled = task.cancel()
            if not cancelled:
                self.logger.error(
                    "Task was not cancelled",
                    name=name
                )

                return
            
            self.logger.debug(
                "Task cancelled successfully",
                name=name
            )

        self._tasks.clear()

        self.logger.debug(
            "All tasks cancelled successfully"
        )