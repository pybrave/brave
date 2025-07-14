# brave/workflow_event_system.py

import asyncio
import time
import json
import socket
import os
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, Coroutine, Union, Literal
from fastapi import Request
from starlette.responses import StreamingResponse

# Type alias
Callback = Union[Callable[[dict], None], Callable[[dict], Coroutine]]

# ================================
# PubSubManager
# ================================
class PubSubManager:
    def __init__(self):
        self.subscribers: dict[str, set[Callback]] = defaultdict(set)

    def subscribe(self, topic: str, callback: Callback):
        self.subscribers[topic].add(callback)

    def unsubscribe(self, topic: str, callback: Callback):
        self.subscribers[topic].discard(callback)

    async def publish(self, topic: str, message: dict):
        for cb in list(self.subscribers.get(topic, [])):
            try:
                if asyncio.iscoroutinefunction(cb):
                    await cb(message)
                else:
                    cb(message)
            except Exception as e:
                print(f"[PubSub ERROR] {e}")


# ================================
# WorkflowQueueManager
# ================================
@dataclass
class WorkflowQueue:
    queue: asyncio.Queue
    task: asyncio.Task
    last_active: float = field(default_factory=time.time)
    subscribers: int = 0

class WorkflowQueueManager:
    def __init__(self, pubsub: PubSubManager):
        self.workflow_map: dict[str, WorkflowQueue] = {}
        self.pubsub = pubsub

    def register(self, workflow_id: str):
        if workflow_id not in self.workflow_map:
            queue = asyncio.Queue()
            task = asyncio.create_task(self._consume_loop(workflow_id, queue))
            self.workflow_map[workflow_id] = WorkflowQueue(queue=queue, task=task)

    async def put(self, workflow_id: str, msg: dict):
        self.register(workflow_id)
        wfq = self.workflow_map[workflow_id]
        wfq.last_active = time.time()
        await wfq.queue.put(msg)

    def get(self, workflow_id: str) -> WorkflowQueue:
        return self.workflow_map[workflow_id]

    async def _consume_loop(self, workflow_id: str, queue: asyncio.Queue):
        while True:
            msg = await queue.get()
            try:
                await self.pubsub.publish(workflow_id, msg)
            except Exception as e:
                print(f"[Consumer ERROR] workflow {workflow_id}: {e}")

    async def cleanup(self, timeout: int = 300):
        now = time.time()
        to_delete = []
        for wf_id, wfq in self.workflow_map.items():
            if wfq.subscribers == 0 and wfq.queue.empty() and (now - wfq.last_active > timeout):
                wfq.task.cancel()
                to_delete.append(wf_id)
        for wf_id in to_delete:
            del self.workflow_map[wf_id]
            print(f"[Cleanup] Removed workflow {wf_id}")


# ================================
# SSEManager
# ================================
class SSEManager:
    def __init__(self, wq_manager: WorkflowQueueManager):
        self.wq_manager = wq_manager

    def create_endpoint(self):
        async def sse_endpoint(workflow_id: str, request: Request):
            self.wq_manager.register(workflow_id)
            wfq = self.wq_manager.get(workflow_id)
            wfq.subscribers += 1
            wfq.last_active = time.time()

            async def event_stream():
                try:
                    while True:
                        if await request.is_disconnected():
                            break
                        msg = await wfq.queue.get()
                        yield f"data: {json.dumps(msg)}\n\n"
                finally:
                    wfq.subscribers -= 1
                    wfq.last_active = time.time()

            return StreamingResponse(event_stream(), media_type="text/event-stream")

        return sse_endpoint


# ================================
# UDSListener using asyncio.start_unix_server
# ================================
class UDSListener:
    def __init__(self, uds_path: str, wq_manager: WorkflowQueueManager):
        self.uds_path = uds_path
        self.wq_manager = wq_manager

    async def start(self):
        if os.path.exists(self.uds_path):
            os.remove(self.uds_path)

        server = await asyncio.start_unix_server(self.handle_client, path=self.uds_path)
        print(f"[UDS] Listening at {self.uds_path}")
        async with server:
            await server.serve_forever()

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        try:
            while line := await reader.readline():
                try:
                    msg = json.loads(line.decode().strip())
                    workflow_id = msg.get("workflow_id", "global")
                    await self.wq_manager.put(workflow_id, msg)
                except Exception as e:
                    print(f"[UDS] Message error: {e}")
        except Exception as e:
            print(f"[UDS] Client error: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
