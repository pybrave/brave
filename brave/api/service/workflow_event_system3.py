# brave/workflow_events/__init__.py
# 空文件，用于模块识别


# brave/workflow_events/types.py
from typing import TypedDict, Optional

class EventMessage(TypedDict):
    workflow_id: str
    event: str
    timestamp: str
    msg: Optional[str]
    level: Optional[str]


# brave/workflow_events/pubsub.py
from collections import defaultdict
from typing import Callable, Awaitable, Dict, List, Any

Subscriber = Callable[[Any], Awaitable[None]]

class PubSubManager:
    def __init__(self):
        self.subscribers: Dict[str, List[Subscriber]] = defaultdict(list)

    def subscribe(self, topic: str, callback: Subscriber):
        self.subscribers[topic].append(callback)

    async def publish(self, topic: str, message: Any):
        for cb in self.subscribers.get(topic, []):
            await cb(message)


# brave/workflow_events/workflow_queue.py
import asyncio
from collections import defaultdict
from typing import Dict, Any
import time
from dataclasses import dataclass, field

@dataclass
class WorkflowQueue:
    queue: asyncio.Queue
    task: asyncio.Task
    last_active: float = field(default_factory=time.time)
    subscribers: int = 0

class WorkflowQueueManager:
    def __init__(self, pubsub):
        self.workflow_map: Dict[str, WorkflowQueue] = {}
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


# brave/workflow_events/uds_listener.py
import os
import asyncio
import json
from .event_router import EventRouter

class UDSListener:
    def __init__(self, uds_path: str, router: EventRouter):
        self.uds_path = uds_path
        self.router = router

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
                    await self.router.dispatch(msg)
                except Exception as e:
                    print(f"[UDS] Message error: {e}")
        except Exception as e:
            print(f"[UDS] Client error: {e}")
        finally:
            writer.close()
            await writer.wait_closed()


# brave/workflow_events/event_router.py
from .workflow_queue import WorkflowQueueManager
from .pubsub import PubSubManager

class EventRouter:
    def __init__(self, pubsub: PubSubManager, wq_manager: WorkflowQueueManager):
        self.pubsub = pubsub
        self.wq_manager = wq_manager

    async def dispatch(self, msg: dict):
        workflow_id = msg.get("workflow_id", "global")
        await self.wq_manager.put(workflow_id, msg)


# brave/workflow_events/sse.py
from fastapi import Request
from fastapi.responses import StreamingResponse
import asyncio
import json
import time

class SSEManager:
    def __init__(self, wq_manager):
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


# brave/workflow_events/manager.py
from .pubsub import PubSubManager
from .workflow_queue import WorkflowQueueManager
from .event_router import EventRouter
from .uds_listener import UDSListener
from .sse import SSEManager

class WorkflowEventSystem:
    def __init__(self, uds_path="/tmp/brave.sock"):
        self.pubsub = PubSubManager()
        self.queue_manager = WorkflowQueueManager(self.pubsub)
        self.router = EventRouter(self.pubsub, self.queue_manager)
        self.uds_listener = UDSListener(uds_path, self.router)
        self.sse = SSEManager(self.queue_manager)

    async def start(self):
        await self.uds_listener.start()

    def sse_endpoint(self):
        return self.sse.create_endpoint()

    def register_subscriber(self, topic: str, callback):
        self.pubsub.subscribe(topic, callback)
