
from typing import Callable, Awaitable, Dict
import asyncio

class WorkflowEventRouter:
    def __init__(self):
        self._handlers: Dict[str, Callable[[dict], Awaitable]] = {}

    def on_event(self, event: str):
        def decorator(func: Callable[[dict], Awaitable]):
            self._handlers[event] = func
            return func
        return decorator

    async def dispatch(self, msg: dict):
        event = msg.get("event")
        if not event:
            print("[EventRouter] No 'event' in message")
            return
        handler = self._handlers.get(event)
        if handler:
            await handler(msg)
        else:
            print(f"[EventRouter] No handler for event '{event}'")
