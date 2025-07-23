
import asyncio
from typing import Generic, TypeVar

from brave.api.core.base_event_router import BaseEventRouter
from typing import Callable, Awaitable, Coroutine, Union

Callback = Union[Callable[[dict], None], Callable[[dict], Coroutine]]


E = TypeVar("E")  # 事件类型（如 Enum）
# F = TypeVar("F")
class DirectDispatch(BaseEventRouter[E,Callback]):
    async def dispatch(self, event: E, msg: dict):
        handlers = self._handlers.get(event, [])
        for handler in handlers:
            if asyncio.iscoroutinefunction(handler):
                await handler(msg)
            else:
                handler(msg)
