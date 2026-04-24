import asyncio
from typing import Dict, Callable

from structlog.typing import FilteringBoundLogger

from .worker import SimpleWorker


class SimpleWorkerManager:

    def __init__(self, logger: FilteringBoundLogger):
        self._workers: Dict[str, SimpleWorker] = {}
        self._logger = logger

    def register(self, worker: SimpleWorker):
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
                    event="Worker crashed",
                    worker=name,
                    error=str(exc)
                )
        return _on_done

    def start_all(self):
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

    def stop_all(self):
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