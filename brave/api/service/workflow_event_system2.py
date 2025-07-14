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

class WorkflowQueueManager:
    def __init__(self, pubsub):
        self.queues: Dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)
        self.pubsub = pubsub
        self._started = False

    async def put(self, workflow_id: str, msg: dict):
        await self.queues[workflow_id].put(msg)

    async def _consume_loop(self, workflow_id: str):
        queue = self.queues[workflow_id]
        while True:
            msg = await queue.get()
            await self.pubsub.publish(msg.get("event", "default"), msg)

    def start(self):
        if self._started:
            return
        self._started = True
        for workflow_id in self.queues:
            asyncio.create_task(self._consume_loop(workflow_id))


# brave/workflow_events/uds_listener.py
import os
import asyncio
import socket
import json
from .event_router import EventRouter

class UDSListener:
    def __init__(self, uds_path: str, router: EventRouter):
        self.uds_path = uds_path
        self.router = router

    async def start(self):
        if os.path.exists(self.uds_path):
            os.remove(self.uds_path)

        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(self.uds_path)
        server.listen(5)
        server.setblocking(False)

        loop = asyncio.get_running_loop()
        print(f"[UDS] Listening at {self.uds_path}")

        while True:
            client, _ = await loop.sock_accept(server)
            asyncio.create_task(self._handle_client(client))

    async def _handle_client(self, client: socket.socket):
        loop = asyncio.get_running_loop()
        with client:
            while True:
                try:
                    data = await loop.sock_recv(client, 4096)
                    if not data:
                        break
                    try:
                        msg = json.loads(data.decode())
                        await self.router.dispatch(msg)
                    except Exception as e:
                        print(f"[UDS] Message error: {e}")
                except Exception as e:
                    print(f"[UDS] Client error: {e}")
                    break


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
        self.wq_manager.start()


# brave/workflow_events/sse.py
from fastapi import Request
from fastapi.responses import StreamingResponse
import asyncio

class SSEManager:
    def __init__(self, wq_manager):
        self.wq_manager = wq_manager

    def create_endpoint(self):
        async def endpoint(workflow_id: str, request: Request):
            queue = self.wq_manager.queues[workflow_id]

            async def event_generator():
                while True:
                    if await request.is_disconnected():
                        break
                    try:
                        msg = await asyncio.wait_for(queue.get(), timeout=10)
                        yield f"data: {msg}\n\n"
                    except asyncio.TimeoutError:
                        yield ": keep-alive\n\n"

            return StreamingResponse(event_generator(), media_type="text/event-stream")

        return endpoint


# brave/workflow_events/manager.py
from .pubsub import PubSubManager
from .workflow_queue import WorkflowQueueManager
from .uds_listener import UDSListener
from .event_router import EventRouter
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
