from typing import Callable, Awaitable, Dict, Union, Coroutine
import asyncio
from collections import defaultdict
from brave.api.core.base_event_router import BaseEventRouter
from brave.api.core.event import WorkflowEvent
from brave.api.core.direct_dispatch import DirectDispatch
Callback = Union[Callable[[dict], None], Callable[[dict], Coroutine]]

class WorkflowEventRouter(DirectDispatch[WorkflowEvent]):
    pass
    # def __init__(self):
    #     # self._handlers: Dict[str, Callable[[dict], Awaitable]] = {}
    #     self._handlers: dict[WorkflowEvent, set[Callback]] = defaultdict(set)

    # def on_event(self, event: WorkflowEvent):
    #     def decorator(func: Callback):
    #         self._handlers[event].add(func)
    #         return func
    #     return decorator

    # def register_handler(self, event: WorkflowEvent, handler: Callback):
    #     self._handlers[event].add(handler)


    # async def dispatch(self,event:WorkflowEvent, msg: dict):
    #     # event = msg.get("workflow_event")
    #     # if not event:
    #     #     print("[EventRouter] No 'workflow_event' in message", msg)
    #     #     return
    #     handlers = self._handlers.get(event)
    #     if handlers:
    #         for handler in handlers:
    #             if asyncio.iscoroutinefunction(handler):
    #                 await handler(msg)
    #             else:
    #                 handler(msg)
    #     else:
    #         print(f"[EventRouter] No handler for event '{event}'")

# @lru_cache(maxsize=1)
# def get_router():
#     return WorkflowEventRouter()