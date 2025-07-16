from collections import defaultdict
from enum import Enum
from typing import Callable, Awaitable, Dict, Union, Coroutine
import asyncio


class IngressEvent(str, Enum):
    WORKFLOW_LOG = "workflow_log"
    WORKFLOW_EVENT_FINISHED = "workflow_event_finished"
    WORKFLOW_EVENT_FAILED = "workflow_event_failed"       

Callback = Union[Callable[[dict], None], Callable[[dict], Coroutine]]

class IngressEventRouter:
    def __init__(self):
        self._handlers: dict[str, set[Callback]] = defaultdict(set)

    def register_handler(self, event: IngressEvent, handler: Callback):
        self._handlers[event].add(handler)
    
    async def dispatch(self, msg: dict):
        event_str = msg.get("ingress_event")
        if not event_str:
            print("[IngressEventRouter] No 'event' in message")
            return
        try:
            event = IngressEvent(event_str)
        except ValueError:
            print(f"[IngressEventRouter] Unknown event type '{event_str}'")
            return
        
        handlers = self._handlers.get(event)
        if handlers:
            for handler in handlers:
                if asyncio.iscoroutinefunction(handler):
                    await handler(msg)
                else:
                    handler(msg)
        else:
            print(f"[IngressEventRouter] No handler for event '{event}'")

# from .workflow_queue import WorkflowQueueManager

# class IngressEventRouter:
#     def __init__(self, wq_manager: WorkflowQueueManager):
#         self.wq_manager = wq_manager

#     async def dispatch(self, msg: dict):
#         workflow_id = msg.get("workflow_id", "global")
#         await self.wq_manager.put(workflow_id, msg)
    