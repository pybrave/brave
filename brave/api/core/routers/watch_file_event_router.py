from typing import Callable, Awaitable, Dict, Union, Coroutine
import asyncio
from collections import defaultdict

from brave.api.core.base_event_router import BaseEventRouter
from brave.api.core.event import WatchFileEvent

Callback = Union[Callable[[dict], None], Callable[[dict], Coroutine]]

class WatchFileEvenetRouter(BaseEventRouter[WatchFileEvent,Callback]):
    async def dispatch(self, event: WatchFileEvent, payload: dict):
        handlers = self._handlers.get(event, [])
        for handler in handlers:
            if asyncio.iscoroutinefunction(handler):
                await handler(payload)
            else:
                handler(payload)
    # def __init__(self):
    #     self._handlers: dict[WatchFileEvent, set[Callback]] = defaultdict(set)

    # def on_event(self, event: WatchFileEvent):
    #     def decorator(func: Callback):
    #         self._handlers[event].add(func)
    #         return func
    #     return decorator

    # def register_handler(self, event: WatchFileEvent, handler: Callback):
    #     self._handlers[event].add(handler)


    # async def dispatch(self, event:WatchFileEvent,msg: dict):
    #     # event = msg.get("file_type")
    #     # if not event:
    #     #     print("[WatchFileEvenetRouter] No 'file_type' in message", msg)
    #     #     return
    #     handlers = self._handlers.get(event)
    #     if handlers:
    #         for handler in handlers:
    #             if asyncio.iscoroutinefunction(handler):
    #                 await handler(msg)
    #             else:
    #                 handler(msg)
    #     else:
    #         print(f"[WatchFileEvenetRouter] No handler for event '{event}'")

