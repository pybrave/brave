from abc import ABC, abstractmethod
import asyncio
from collections import defaultdict
from ctypes import Union
from typing import Any, Callable, Awaitable, Coroutine, Optional, Type, TypeVar, Generic, Union, Dict, Set

from pydantic import BaseModel

from brave.api.core.event import WorkflowEvent
E = TypeVar("E")  # 事件类型（如 Enum）
F = TypeVar("F", bound=Callable[..., Any])  
# Callback = Union[Callable[[dict], None], Callable[[dict], Coroutine],Callable[[str,dict], Coroutine]]
P = TypeVar("P", bound=BaseModel)

class BaseEventRouter(ABC, Generic[E,F]):
    def __init__(self):
        # self._handlers: Dict[str, Callable[[dict], Awaitable]] = {}
        self._handlers: dict[E, set[F]] = defaultdict(set)
        # self._payload_types: Dict[E, Type[BaseModel]] = {}

    def on_event2(self, event: E):
        def decorator(func: F):
            self._handlers[event].add(func)
            return func
        return decorator


    def on_event(self, event_type: E):
        def decorator(func:F):
            self._handlers[event_type].add(func)
            # if payload_type:
            #     self._payload_types[event_type] = payload_type
            # return func
        return decorator

    def register_handler(self, event: E, handler: F):
        self._handlers[event].add(handler)

    async def dispatch(self, event: E, *payload: BaseModel):
        handlers = self._handlers.get(event, [])
        # expected_type = self._payload_types.get(event)
        # if  expected_type:
        #     if not isinstance(payload, expected_type):
        #         raise TypeError(f"[EventRouter] Expected payload type {expected_type}, got {type(payload)}")

        for handler in handlers:
            if asyncio.iscoroutinefunction(handler):
                await handler(*payload)
            else:
                handler(*payload)
        else:
            print(f"[BaseEventRouter] No handler for event '{event}'")
            
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
