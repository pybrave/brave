
import asyncio
from typing import Generic, TypeVar

from brave.api.core.base_event_router import BaseEventRouter


E = TypeVar("E")  # 事件类型（如 Enum）
class DirectDispatch(BaseEventRouter[E]):
    async def dispatch(self, event: E, msg: dict):
        handlers = self._handlers.get(event, [])
        for handler in handlers:
            if asyncio.iscoroutinefunction(handler):
                await handler(msg)
            else:
                handler(msg)
