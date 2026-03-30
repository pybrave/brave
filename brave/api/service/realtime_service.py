from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Literal


class RealtimeService(ABC):
    endpoint_transport: Literal["http", "websocket"] = "http"

    @abstractmethod
    async def push_message(self, msg: Dict[str, Any]):
        raise NotImplementedError

    @abstractmethod
    async def push_message_default(self, msg: Dict[str, Any]):
        raise NotImplementedError

    @abstractmethod
    async def broadcast_loop(self):
        raise NotImplementedError

    @abstractmethod
    def create_endpoint(self) -> Callable[..., Any]:
        raise NotImplementedError
