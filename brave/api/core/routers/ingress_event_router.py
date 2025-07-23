from collections import defaultdict
from enum import Enum
from typing import Callable, Awaitable, Dict, Union, Coroutine
import asyncio

from brave.api.core.base_event_router import BaseEventRouter
from brave.api.core.direct_dispatch import DirectDispatch
from brave.api.core.event import IngressEvent
from brave.api.core.queued_dispatch import QueuedDispatch


Callback = Union[Callable[[dict], None], Callable[[dict], Coroutine]]

class IngressEventRouter(BaseEventRouter[IngressEvent,Callback]):
    async def dispatch(self, event: IngressEvent, payload: dict):
        handlers = self._handlers.get(event, [])
        for handler in handlers:
            if asyncio.iscoroutinefunction(handler):
                await handler(payload)
            else:
                handler(payload)
    # def __init__(self):
    #     super().__init__(maxlen=100, delay=0.02)

    # def __init__(self):
    #     self._handlers: dict[IngressEvent, set[Callback]] = defaultdict(set)

    # def register_handler(self, event: IngressEvent, handler: Callback):
    #     self._handlers[event].add(handler)
    
    # async def dispatch(self, event: IngressEvent, msg: dict):
    #     # event_str = msg.get("ingress_event")
    #     # if not event_str:
    #     #     print("[IngressEventRouter] No 'ingress_event' in message")
    #     #     return
        
    #     # data = msg.get("data")
    #     # if not data:
    #     #     print("[IngressEventRouter] No 'data' in message")
    #     #     return
        
    #     # try:
    #     #     event = IngressEvent(event_str)
    #     # except ValueError:
    #     #     print(f"[IngressEventRouter] Unknown event type '{event_str}'", msg)
    #     #     return
        
    #     handlers = self._handlers.get(event)
    #     if handlers:
    #         for handler in handlers:
    #             if asyncio.iscoroutinefunction(handler):
    #                 await handler(msg)
    #             else:
    #                 handler(msg)
    #     else:
    #         print(f"[IngressEventRouter] No handler for event '{event}'")

# from .workflow_queue import WorkflowQueueManager

# class IngressEventRouter:
#     def __init__(self, wq_manager: WorkflowQueueManager):
#         self.wq_manager = wq_manager

#     async def dispatch(self, msg: dict):
#         workflow_id = msg.get("workflow_id", "global")
#         await self.wq_manager.put(workflow_id, msg)
    