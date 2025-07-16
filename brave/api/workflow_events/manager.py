# from brave.api.core.pubsub import PubSubManager
# from brave.api.ingress.interfaces.base_ingress import BaseMessageIngress
# from .workflow_queue import WorkflowQueueManager
# from .uds_listener import UDSListener
# from .sse import SSEManager
# import asyncio
# from typing import Union, Optional

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
# from brave.api.core.pubsub import PubSubManager
# from .workflow_queue import WorkflowQueueManager
# from brave.api.core.ingress_event_router import IngressEventRouter
# from .sse import SSEManager
# from brave.api.ingress.http_ingress import HTTPIngress
# from dependency_injector.wiring import inject, Provide
# from brave.app_container import AppContainer
# # from .config import EVENT_MODE, UDS_PATH
# EVENT_MODE = "stream"
# UDS_PATH = "/tmp/brave.sock"

# class WorkflowManager:
#     @inject
#     def __init__(
#         self, 
#         queue_manager: WorkflowQueueManager = Provide[AppContainer.workflow_queue_manager], 
#         pubsub: PubSubManager = Provide[AppContainer.pubsub_manager]):

#         self.pubsub = pubsub
#         self.queue_manager = queue_manager
#         self.sse = SSEManager(self.queue_manager)

#     # async def start(self):
#     #     if isinstance(self.ingress, BaseMessageIngress):
#     #         await self.ingress.start()

#     # def register_http(self, app):
#     #     if isinstance(self.ingress, HTTPIngress):
#     #         self.ingress.register(app)

#     def sse_endpoint(self):
#         return self.sse.create_endpoint()

#     def register_subscriber(self, topic: str, callback):
#         self.pubsub.subscribe(topic, callback)

#     async def cleanup_loop(self):
#         while True:
#             await self.queue_manager.cleanup()
#             await asyncio.sleep(10)




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