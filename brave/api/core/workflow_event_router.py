from typing import Callable, Awaitable, Dict, Union, Coroutine
import asyncio
from collections import defaultdict

Callback = Union[Callable[[dict], None], Callable[[dict], Coroutine]]

class WorkflowEventRouter:
    def __init__(self):
        # self._handlers: Dict[str, Callable[[dict], Awaitable]] = {}
        self._handlers: dict[str, set[Callback]] = defaultdict(set)

    def on_event(self, event: str):
        def decorator(func: Callback):
            self._handlers[event].add(func)
            return func
        return decorator

    async def dispatch(self, msg: dict):
        event = msg.get("workflow_event")
        if not event:
            print("[EventRouter] No 'event' in message")
            return
        handlers = self._handlers.get(event)
        if handlers:
            for handler in handlers:
                if asyncio.iscoroutinefunction(handler):
                    await handler(msg)
                else:
                    handler(msg)
        else:
            print(f"[EventRouter] No handler for event '{event}'")

# @lru_cache(maxsize=1)
# def get_router():
#     return WorkflowEventRouter()