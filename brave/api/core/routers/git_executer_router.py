
import asyncio
from typing import Callable, Awaitable, Dict, Union, Coroutine

from brave.api.core.event import AnalysisExecutorEvent, GitExecutorEvent
from brave.api.core.base_event_router import BaseEventRouter
Callback = Union[Callable[[dict], None], Callable[[dict], Coroutine]]

    
class GitExecuterRouter(BaseEventRouter[AnalysisExecutorEvent,Callback]):
    async def dispatch(self, event: GitExecutorEvent, payload: dict):
        handlers = self._handlers.get(event, [])
        if handlers:
            for handler in handlers:
                if asyncio.iscoroutinefunction(handler):
                    await handler(payload)
                else:
                    handler(payload)