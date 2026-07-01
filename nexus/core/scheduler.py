"""Scheduler — async task execution for long-running workflows.

Many Nexus operations (literature search, RAG indexing, multi-step
reasoning, report generation) are long-running and benefit from
concurrent execution. The Scheduler provides a small, typed abstraction
over :mod:`asyncio` that supports:

- Submitting tasks with priorities
- Awaiting results (or cancellation)
- Tracking task status (pending, running, done, failed, cancelled)

The Scheduler is intentionally minimal. It is not a job queue for
production multi-node deployments — for that, plug in Celery, RQ, or
Dramatiq via the plugin system. The in-process Scheduler is sufficient
for single-process workflows and for testing.
"""

from __future__ import annotations

import asyncio
import contextlib
import time
import uuid
from collections.abc import Awaitable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task(Generic[T]):
    id: str
    name: str
    priority: int
    status: TaskStatus = TaskStatus.PENDING
    result: T | None = None
    error: Exception | None = None
    submitted_at: float = field(default_factory=time.time)
    started_at: float | None = None
    completed_at: float | None = None

    def duration(self) -> float | None:
        if self.started_at is None:
            return None
        end = self.completed_at or time.time()
        return end - self.started_at


class Scheduler:
    """Async task scheduler.

    The Scheduler runs tasks on a single event loop. Tasks are executed
    in priority order (lower priority value = higher priority). Each
    task is wrapped in :meth:`_run_task` which updates its status and
    captures exceptions.

    Example:
        >>> async def main():
        ...     sched = Scheduler()
        ...     tid = sched.submit("compute", some_coroutine(), priority=1)
        ...     result = await sched.await_result(tid)
        ...     return result
    """

    def __init__(self, max_concurrency: int = 8) -> None:
        if max_concurrency < 1:
            raise ValueError("max_concurrency must be >= 1")
        self._max_concurrency = max_concurrency
        self._tasks: dict[str, Task[Any]] = {}
        self._futures: dict[str, asyncio.Future[Any]] = {}
        self._queue: asyncio.PriorityQueue[tuple[int, float, str]] = asyncio.PriorityQueue()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._worker: asyncio.Task[None] | None = None
        self._stopped = False

    @property
    def max_concurrency(self) -> int:
        return self._max_concurrency

    def submit(
        self,
        name: str,
        coro: Awaitable[T],
        priority: int = 10,
    ) -> str:
        """Submit a coroutine for execution. Returns the task ID.

        The coroutine is not started immediately; it is enqueued and
        picked up by the worker when a concurrency slot is available.
        """
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        task: Task[T] = Task(id=task_id, name=name, priority=priority)
        self._tasks[task_id] = task

        loop = self._ensure_loop()
        future: asyncio.Future[T] = loop.create_future()
        self._futures[task_id] = future

        # Wrap the awaitable so the worker can track start/end.
        async def _wrapped() -> T:
            task.status = TaskStatus.RUNNING
            task.started_at = time.time()
            try:
                result = await coro
                task.result = result
                task.status = TaskStatus.DONE
                task.completed_at = time.time()
                return result
            except asyncio.CancelledError:
                task.status = TaskStatus.CANCELLED
                task.completed_at = time.time()
                raise
            except Exception as exc:
                task.error = exc
                task.status = TaskStatus.FAILED
                task.completed_at = time.time()
                raise
            finally:
                if not future.done():
                    if task.status == TaskStatus.DONE and task.result is not None:
                        future.set_result(task.result)
                    elif task.status == TaskStatus.FAILED and task.error is not None:
                        future.set_exception(task.error)

        # Enqueue: (priority, submission_time, task_id) — FIFO within priority.
        self._queue.put_nowait((priority, time.time(), task_id))
        self._tasks[task_id].__dict__["_coro"] = _wrapped  # stash for worker
        self._ensure_worker()
        return task_id

    async def await_result(self, task_id: str, timeout: float | None = None) -> Any:
        """Await a submitted task's result."""
        if task_id not in self._futures:
            raise KeyError(f"Unknown task {task_id}")
        fut = self._futures[task_id]
        if timeout is None:
            return await fut
        return await asyncio.wait_for(fut, timeout=timeout)

    def get_task(self, task_id: str) -> Task[Any]:
        if task_id not in self._tasks:
            raise KeyError(f"Unknown task {task_id}")
        return self._tasks[task_id]

    def list_tasks(self, status: TaskStatus | None = None) -> list[Task[Any]]:
        tasks = list(self._tasks.values())
        if status is not None:
            tasks = [t for t in tasks if t.status == status]
        return sorted(tasks, key=lambda t: t.submitted_at)

    def cancel(self, task_id: str) -> bool:
        if task_id not in self._tasks:
            return False
        task = self._tasks[task_id]
        if task.status in (TaskStatus.DONE, TaskStatus.FAILED, TaskStatus.CANCELLED):
            return False
        fut = self._futures.get(task_id)
        if fut is not None and not fut.done():
            fut.cancel()
            task.status = TaskStatus.CANCELLED
            task.completed_at = time.time()
            return True
        return False

    async def shutdown(self) -> None:
        self._stopped = True
        if self._worker is not None:
            self._worker.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._worker
            self._worker = None

    # ── Internals ─────────────────────────────────────────────────────

    def _ensure_loop(self) -> asyncio.AbstractEventLoop:
        if self._loop is None:
            self._loop = asyncio.get_event_loop()
        return self._loop

    def _ensure_worker(self) -> None:
        if self._worker is not None:
            return
        loop = self._ensure_loop()
        self._worker = loop.create_task(self._worker_loop())

    async def _worker_loop(self) -> None:
        """Worker that pulls tasks from the priority queue and runs them.

        Respects max_concurrency by tracking the number of in-flight tasks.
        """
        in_flight: set[asyncio.Task[Any]] = set()
        while not self._stopped:
            try:
                _priority, _submitted, task_id = await asyncio.wait_for(
                    self._queue.get(), timeout=0.1
                )
            except asyncio.TimeoutError:
                # Allow in-flight tasks to complete; then re-check queue.
                if in_flight:
                    _done, in_flight = await asyncio.wait(
                        in_flight, return_when=asyncio.FIRST_COMPLETED, timeout=0.1
                    )
                continue

            task = self._tasks[task_id]
            coro_factory = task.__dict__.get("_coro")
            if coro_factory is None:
                continue

            # Wait if at concurrency limit.
            while len(in_flight) >= self._max_concurrency:
                _done, in_flight = await asyncio.wait(
                    in_flight, return_when=asyncio.FIRST_COMPLETED
                )

            async_task = asyncio.create_task(coro_factory())
            in_flight.add(async_task)

            # Propagate result/cancellation to the stored future.
            def _propagate(t: asyncio.Task[Any], tid: str = task_id) -> None:
                fut = self._futures.get(tid)
                if fut is None or fut.done():
                    return
                if t.cancelled():
                    fut.cancel()
                    return
                exc = t.exception()
                if exc is not None:
                    fut.set_exception(exc)
                else:
                    fut.set_result(t.result())

            async_task.add_done_callback(_propagate)


__all__ = ["Scheduler", "Task", "TaskStatus"]
