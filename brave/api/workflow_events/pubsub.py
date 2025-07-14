from collections import defaultdict
from typing import Callable, Awaitable, Dict, List, Any, Union, Coroutine
import asyncio

Callback = Union[Callable[[dict], None], Callable[[dict], Coroutine]]

class PubSubManager:
    def __init__(self):
        self.subscribers: dict[str, set[Callback]] = defaultdict(set)

    def subscribe(self, topic: str, callback: Callback):
        self.subscribers[topic].add(callback)

    def unsubscribe(self, topic: str, callback: Callback):
        self.subscribers[topic].discard(callback)

    async def publish(self, topic: str, message: dict):
        for cb in list(self.subscribers.get(topic, [])):
            try:
                if asyncio.iscoroutinefunction(cb):
                    await cb(message)
                else:
                    cb(message)
            except Exception as e:
                print(f"[PubSub ERROR] {e}")
