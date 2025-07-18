from abc import ABC, abstractmethod
import asyncio
from collections import defaultdict
from ctypes import Union
from typing import Callable, Awaitable, Coroutine, TypeVar, Generic, Union, Dict, Set

from brave.api.core.event import WorkflowEvent
E = TypeVar("E")  # 事件类型（如 Enum）

Callback = Union[Callable[[dict], None], Callable[[dict], Coroutine]]

class BaseEventRouter(ABC, Generic[E]):
    def __init__(self):
        # self._handlers: Dict[str, Callable[[dict], Awaitable]] = {}
        self._handlers: dict[E, set[Callback]] = defaultdict(set)

    def on_event(self, event: E):
        def decorator(func: Callback):
            self._handlers[event].add(func)
            return func
        return decorator

    def register_handler(self, event: E, handler: Callback):
        self._handlers[event].add(handler)


    # async def dispatch(self,event:E, msg: dict):
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
