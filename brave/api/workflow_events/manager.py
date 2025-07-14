from brave.api.workflow_events.interfaces.base_ingress import BaseMessageIngress
from .pubsub import PubSubManager
from .workflow_queue import WorkflowQueueManager
from .uds_listener import UDSListener
from .event_router import EventRouter
from .sse import SSEManager


#                         [ workflow_queues ]
#                           ┌────────────┐
# [ UDS Producer ] ───→──→─▶ wf-123 → Queue ──┐
#                           └────────────┘    │
#                                             ▼
#                                    [ 消费 Task: while True get() ]
#                                             │
#                                             ▼
#                                    pubsub.publish(wf-123, msg)
#                                             │
#                 ┌───────────────────────────┼────────────────────────┐
#                 ▼                           ▼                        ▼
#       Log模块订阅器                  指标模块订阅器              告警模块订阅器



# [ Nextflow #1 ]──┐
# [ Nextflow #2 ]──┼──▶  /tmp/nextflow.sock
# [ Nextflow #N ]──┘         ▲
#                            │
#              [FastAPI UDS Server]
#                       │
#             +─────────┴─────────+
#             │ asyncio.Queue/msg │
#             │   optional logic  │
#             └─────▶ SSE 推送 ───┘


#  [Producer] --->
#                \
#  [Producer] ---> \                     ┌────────────┐
#                    --> [UDS Server] -->│  asyncio   │
#  [Producer] ---> /                     │   Queue    │--> 处理 / 落盘 / SSE
#                /                       └────────────┘
#  [Producer] --->


# UDSListener
#    ↓
# EventRouter
#    ↓
# WorkflowQueueManager
#    ↓
# PubSubManager
from .pubsub import PubSubManager
from .workflow_queue import WorkflowQueueManager
from .event_router import EventRouter
from .sse import SSEManager
from .ingress.factory import create_ingress
from .ingress.http_ingress import HTTPIngress
from typing import Union
# from .config import EVENT_MODE, UDS_PATH
EVENT_MODE = "stream"
UDS_PATH = "/tmp/brave.sock"

class WorkflowEventSystem:
    def __init__(self):
        self.pubsub = PubSubManager()
        self.queue_manager = WorkflowQueueManager(self.pubsub)
        self.router = EventRouter(self.pubsub, self.queue_manager)
        self.ingress = create_ingress(EVENT_MODE, UDS_PATH, self.router)
        self.sse = SSEManager(self.queue_manager)

    async def start(self):
        if isinstance(self.ingress, BaseMessageIngress):
            await self.ingress.start()

    def register_http(self, app):
        if isinstance(self.ingress, HTTPIngress):
            self.ingress.register(app)

    def sse_endpoint(self):
        return self.sse.create_endpoint()

    def register_subscriber(self, topic: str, callback):
        self.pubsub.subscribe(topic, callback)


# class WorkflowEventSystem:
#     def __init__(self, uds_path="/tmp/brave.sock"):
#         self.pubsub = PubSubManager()
#         self.queue_manager = WorkflowQueueManager(self.pubsub)
#         self.router = EventRouter(self.pubsub, self.queue_manager)
#         self.uds_listener = UDSListener(uds_path, self.router)
#         self.sse = SSEManager(self.queue_manager)

#     async def start(self):
#         await self.uds_listener.start()

#     def sse_endpoint(self):
#         return self.sse.create_endpoint()

#     def register_subscriber(self, topic: str, callback):
#         self.pubsub.subscribe(topic, callback)

# class WorkflowEventSystem:
#     def __init__(self, uds_path="/tmp/brave.sock"):
#         self.pubsub = PubSubManager()
#         self.queue_manager = WorkflowQueueManager(self.pubsub)
#         self.router = EventRouter(self.pubsub, self.queue_manager)
#         self.uds_listener = UDSListener(uds_path, self.router)
#         self.sse = SSEManager(self.queue_manager)

#     async def start(self):
#         await self.uds_listener.start()

#     def sse_endpoint(self):
#         return self.sse.create_endpoint()