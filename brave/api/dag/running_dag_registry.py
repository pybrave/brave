import asyncio
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional


@dataclass
class RunningDagEntry:
    analysis_id: str
    task_name: str
    source: str
    started_at: float
    updated_at: float
    max_concurrency: int
    queue_size: int
    poll_interval_seconds: float
    timeout_seconds: Optional[int]
    status: str = "running"
    dag_complete_event_at: Optional[float] = None


class RunningDagRegistry:
    """In-memory registry for currently running DAG tasks in this process."""

    def __init__(self, max_recent_records: int = 200):
        self._lock = asyncio.Lock()
        self._running: dict[str, RunningDagEntry] = {}
        self._tasks: dict[str, asyncio.Task] = {}
        self._stop_callbacks: dict[str, Callable[[], None]] = {}
        self._recent: dict[str, dict[str, Any]] = {}
        self._recent_order: list[str] = []
        self._max_recent_records = max(max_recent_records, 1)

    async def register(
        self,
        analysis_id: str,
        *,
        task_name: str,
        source: str,
        max_concurrency: int,
        queue_size: int,
        poll_interval_seconds: float,
        timeout_seconds: Optional[int],
        task: Optional[asyncio.Task] = None,
        stop_callback: Optional[Callable[[], None]] = None,
    ) -> dict[str, Any]:
        now = time.time()
        entry = RunningDagEntry(
            analysis_id=analysis_id,
            task_name=task_name,
            source=source,
            started_at=now,
            updated_at=now,
            max_concurrency=max_concurrency,
            queue_size=queue_size,
            poll_interval_seconds=poll_interval_seconds,
            timeout_seconds=timeout_seconds,
        )
        async with self._lock:
            self._running[analysis_id] = entry
            if task is not None:
                self._tasks[analysis_id] = task
            if stop_callback is not None:
                self._stop_callbacks[analysis_id] = stop_callback
            return self._entry_to_dict(entry)

    async def mark_dag_complete_event(self, analysis_id: str) -> Optional[dict[str, Any]]:
        async with self._lock:
            entry = self._running.get(analysis_id)
            if not entry:
                return None
            now = time.time()
            entry.dag_complete_event_at = now
            entry.updated_at = now
            return self._entry_to_dict(entry)

    async def mark_finished(self, analysis_id: str, *, result: Optional[dict[str, Any]] = None) -> None:
        await self._mark_terminal(analysis_id, status="done", result=result, error=None)

    async def mark_failed(self, analysis_id: str, *, error: str) -> None:
        await self._mark_terminal(analysis_id, status="failed", result=None, error=error)

    async def _mark_terminal(
        self,
        analysis_id: str,
        *,
        status: str,
        result: Optional[dict[str, Any]],
        error: Optional[str],
    ) -> None:
        now = time.time()
        async with self._lock:
            entry = self._running.pop(analysis_id, None)
            self._tasks.pop(analysis_id, None)
            self._stop_callbacks.pop(analysis_id, None)
            if entry:
                record = {
                    **self._entry_to_dict(entry),
                    "status": status,
                    "finished_at": now,
                    "duration_seconds": round(max(now - entry.started_at, 0.0), 3),
                    "result": result,
                    "error": error,
                }
            else:
                record = {
                    "analysis_id": analysis_id,
                    "status": status,
                    "finished_at": now,
                    "duration_seconds": None,
                    "result": result,
                    "error": error,
                }

            self._recent[analysis_id] = record
            self._recent_order = [item for item in self._recent_order if item != analysis_id]
            self._recent_order.append(analysis_id)

            while len(self._recent_order) > self._max_recent_records:
                expired_id = self._recent_order.pop(0)
                self._recent.pop(expired_id, None)

    async def get_running(self, analysis_id: str) -> Optional[dict[str, Any]]:
        async with self._lock:
            entry = self._running.get(analysis_id)
            if not entry:
                return None
            return self._entry_to_dict(entry)

    async def list_running(self) -> list[dict[str, Any]]:
        async with self._lock:
            entries = [self._entry_to_dict(item) for item in self._running.values()]
        return sorted(entries, key=lambda x: x["started_at"])

    async def get_recent(self, analysis_id: str) -> Optional[dict[str, Any]]:
        async with self._lock:
            record = self._recent.get(analysis_id)
            if not record:
                return None
            return dict(record)

    async def stop_running(
        self,
        analysis_id: str,
        *,
        timeout_seconds: float = 3.0,
        wait_for_completion: bool = True,
        cancel_on_timeout: bool = True,
    ) -> dict[str, Any]:
        task: Optional[asyncio.Task] = None
        stop_callback: Optional[Callable[[], None]] = None
        running_exists = False
        async with self._lock:
            running_exists = analysis_id in self._running
            task = self._tasks.get(analysis_id)
            stop_callback = self._stop_callbacks.get(analysis_id)

        if not running_exists and task is None:
            return {
                "analysis_id": analysis_id,
                "found": False,
                "cancelled": False,
                "reason": "not running",
            }

        graceful_stop_requested = False
        if stop_callback is not None:
            try:
                stop_callback()
                graceful_stop_requested = True
            except Exception:
                pass

        cancelled = False
        timed_out = False
        if task and wait_for_completion:
            if not task.done():
                try:
                    await asyncio.wait_for(task, timeout=timeout_seconds)
                except asyncio.CancelledError:
                    pass
                except asyncio.TimeoutError:
                    timed_out = True
                    if cancel_on_timeout:
                        task.cancel()
                        cancelled = True
                        try:
                            await asyncio.wait_for(task, timeout=max(timeout_seconds / 2.0, 1.0))
                        except Exception:
                            pass
                except Exception:
                    pass

        # If watcher has not yet converted it to terminal state and we forced cancel, mark it.
        if cancelled and await self.get_running(analysis_id):
            await self.mark_failed(analysis_id, error="cancelled by api")

        return {
            "analysis_id": analysis_id,
            "found": True,
            "graceful_stop_requested": graceful_stop_requested,
            "cancelled": cancelled,
            "timed_out": timed_out,
            "reason": "stop requested",
        }

    async def list_recent(self) -> list[dict[str, Any]]:
        async with self._lock:
            return [dict(self._recent[item]) for item in self._recent_order]

    @staticmethod
    def _entry_to_dict(entry: RunningDagEntry) -> dict[str, Any]:
        return {
            "analysis_id": entry.analysis_id,
            "task_name": entry.task_name,
            "source": entry.source,
            "status": entry.status,
            "started_at": entry.started_at,
            "updated_at": entry.updated_at,
            "max_concurrency": entry.max_concurrency,
            "queue_size": entry.queue_size,
            "poll_interval_seconds": entry.poll_interval_seconds,
            "timeout_seconds": entry.timeout_seconds,
            "dag_complete_event_at": entry.dag_complete_event_at,
        }


running_dag_registry = RunningDagRegistry()
