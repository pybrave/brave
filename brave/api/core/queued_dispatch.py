import asyncio
from typing import TypeVar, Generic, Callable, Coroutine, Union, Dict, Set
from collections import defaultdict, deque
from dataclasses import dataclass, field
from brave.api.core.base_event_router import BaseEventRouter

E = TypeVar("E")  # 泛型事件类型
Callback = Union[Callable[[dict], None], Callable[[dict], Coroutine]]

class QueuedDispatch(BaseEventRouter[E,Callback]):
    def __init__(self, *args, maxlen: int = 100, delay: float =0, **kwargs):
        super().__init__(*args, **kwargs)
        self._queues: Dict[E, asyncio.Queue] = {}
        self._tasks: Dict[E, asyncio.Task] = {}
        self.maxlen = maxlen
        self.delay = delay

    async def dispatch(self, event: E, msg: dict):
        if event not in self._queues:
            self._queues[event] = asyncio.Queue(maxsize=self.maxlen)
            self._tasks[event] = asyncio.create_task(self._consume_worker(event))
        await self._queues[event].put(msg)

    async def _consume_worker(self, event: E):
        queue = self._queues[event]
        handlers = self._handlers.get(event, [])
        while True:
            msg = await queue.get()
            for handler in handlers:
                if asyncio.iscoroutinefunction(handler):
                    await handler(msg)
                else:
                    handler(msg)
            await asyncio.sleep(self.delay)
