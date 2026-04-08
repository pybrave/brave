
import asyncio
import time
from dataclasses import dataclass
from typing import Optional

from brave.api.core.evenet_bus import EventBus
from brave.api.core.event import AnalysisExecutorEvent
from brave.api.config.db import get_engine

from brave.api.service import analysis_node_service, analysis_edge_service, analysis_runtime_engine_service, analysis_service
from brave.api.core.routers_name import RoutersName
from brave.app_container import AppContainer
from dependency_injector.wiring import Provide, inject



@dataclass
class _QueuedNode:
    analysis_node_id: str


class RuntimeDagQueueScheduler:
    def __init__(
        self,
        analysis_id: str,
        event_bus: EventBus,
        *,
        max_steps: int,
        max_concurrency: int,
        queue_size: int,
        poll_interval_seconds: float,
        timeout_seconds: Optional[int],
    ):
        self.analysis_id = analysis_id
        self.event_bus = event_bus
        self.max_steps = max(max_steps, 1)
        self.max_concurrency = max(max_concurrency, 1)
        self.queue: asyncio.Queue[_QueuedNode] = asyncio.Queue(maxsize=max(queue_size, 1))
        self.poll_interval_seconds = max(poll_interval_seconds, 0.1)
        self.timeout_seconds = timeout_seconds if timeout_seconds and timeout_seconds > 0 else None

        self.submitted_count = 0
        self.failed_to_submit_count = 0
        self.dispatch_errors: list[dict] = []
        self._workers: list[asyncio.Task] = []
        self._started_at = time.monotonic()

    def _is_timeout(self) -> bool:
        if self.timeout_seconds is None:
            return False
        return (time.monotonic() - self._started_at) >= self.timeout_seconds

    async def _get_snapshot(self) -> dict:
        with get_engine().begin() as conn:
            return analysis_runtime_engine_service.get_runtime_snapshot(conn, analysis_id=self.analysis_id)

    async def _claim_and_enqueue_ready_nodes(self) -> int:
        claimed = 0
        while not self.queue.full() and self.submitted_count < self.max_steps:
            with get_engine().begin() as conn:
                node = analysis_runtime_engine_service.schedule_next(conn, analysis_id=self.analysis_id)

            if not node:
                break

            analysis_node_id = str(node.get("analysis_node_id") or "")
            if not analysis_node_id:
                continue

            await self.queue.put(_QueuedNode(analysis_node_id=analysis_node_id))
            claimed += 1

        return claimed

    async def _dispatch_single_node(self, queued_node: _QueuedNode) -> None:
        with get_engine().begin() as conn:
            node = analysis_node_service.find_by_analysis_node_id(conn, queued_node.analysis_node_id)
            if not node:
                raise ValueError(f"analysis_node not found: {queued_node.analysis_node_id}")

            analysis_executer_modal = await analysis_service.run_analysis_node(conn, node, "node")

        await self.event_bus.dispatch(
            RoutersName.ANALYSIS_EXECUTER_ROUTER,
            AnalysisExecutorEvent.ON_ANALYSIS_NODE_SUBMITTED,
            analysis_executer_modal,
        )

        self.submitted_count += 1

    async def _worker(self) -> None:
        while True:
            queued_node = await self.queue.get()
            try:
                await self._dispatch_single_node(queued_node)
            except Exception as exc:
                self.failed_to_submit_count += 1
                self.dispatch_errors.append(
                    {
                        "analysis_node_id": queued_node.analysis_node_id,
                        "error": str(exc),
                    }
                )
                # 提交阶段失败时，及时回写失败，避免节点永久停留在 running。
                with get_engine().begin() as conn:
                    failed_node = analysis_node_service.find_by_analysis_node_id(conn, queued_node.analysis_node_id)
                    if failed_node:
                        analysis_runtime_engine_service.complete_node(
                            conn,
                            analysis_id=str(failed_node.get("analysis_id") or ""),
                            node_id=str(failed_node.get("node_id") or ""),
                            status="failed",
                            exit_code=1,
                            error_message=f"dispatch failed: {exc}",
                        )
            finally:
                self.queue.task_done()

    async def _start_workers(self) -> None:
        self._workers = [asyncio.create_task(self._worker()) for _ in range(self.max_concurrency)]

    async def _stop_workers(self) -> None:
        for task in self._workers:
            task.cancel()
        if self._workers:
            await asyncio.gather(*self._workers, return_exceptions=True)

    async def run(self) -> dict:
        await self._start_workers()

        timed_out = False
        try:
            while True:
                await self._claim_and_enqueue_ready_nodes()
                snapshot = await self._get_snapshot()
                is_finished = bool(snapshot.get("is_finished"))
                running_count = int(snapshot.get("status_count", {}).get("running", 0))

                if is_finished and self.queue.empty():
                    break

                if self.submitted_count >= self.max_steps and self.queue.empty() and running_count == 0:
                    break

                if self._is_timeout():
                    timed_out = True
                    break

                await asyncio.sleep(self.poll_interval_seconds)

            await self.queue.join()
            final_snapshot = await self._get_snapshot()
            return {
                "analysis_id": self.analysis_id,
                "submitted_count": self.submitted_count,
                "failed_to_submit_count": self.failed_to_submit_count,
                "max_steps": self.max_steps,
                "max_concurrency": self.max_concurrency,
                "queue_size": self.queue.maxsize,
                "timed_out": timed_out,
                "dispatch_errors": self.dispatch_errors,
                "snapshot": final_snapshot,
            }
        finally:
            await self._stop_workers()
            await self.event_bus.dispatch(
                RoutersName.ANALYSIS_EXECUTER_ROUTER,
                AnalysisExecutorEvent.ON_DAG_COMPLETE,
                {
                    "analysis_id": self.analysis_id
                }
            )

