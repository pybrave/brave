import asyncio
import json
from collections import defaultdict
from typing import Any, Dict, Set

from fastapi import WebSocket, WebSocketDisconnect
from brave.api.service.realtime_service import RealtimeService


class WSSessionService(RealtimeService):
    """WebSocket service aligned with SSESessionService's public interface."""

    endpoint_transport = "websocket"

    def __init__(self):
        self.global_queue = asyncio.Queue()
        self.client_groups: Dict[str, Set[WebSocket]] = defaultdict(set)
        self.lock = asyncio.Lock()

    def add_client(self, client: WebSocket, group: str):
        self.client_groups[group].add(client)

    def remove_client(self, client: WebSocket, group: str):
        self.client_groups[group].discard(client)

    async def event_generator(self, websocket: WebSocket, group: str):
        """Keep websocket alive and consume client messages until disconnect."""
        await websocket.accept()
        await websocket.send_json({"type": "ping"})
        try:
            while True:
                try:
                    await asyncio.wait_for(websocket.receive_text(), timeout=10)
                except asyncio.TimeoutError:
                    await websocket.send_json({"type": "ping"})
        except WebSocketDisconnect:
            pass
        finally:
            async with self.lock:
                self.remove_client(websocket, group)

    async def push_message(self, msg: dict):
        # Message shape: {"group": "default", "data": ...}
        await self.global_queue.put(msg)

    async def push_message_default(self, msg: dict):
        # Keep same method as SSESessionService for compatibility.
        await self.global_queue.put({"group": "default", "data": msg})

    async def _send_to_websocket(self, websocket: WebSocket, data: Any):
        if isinstance(data, (dict, list)):
            await websocket.send_json(data)
            return
        if isinstance(data, str):
            try:
                await websocket.send_json(json.loads(data))
                return
            except json.JSONDecodeError:
                await websocket.send_text(data)
                return
        await websocket.send_json(data)

    async def broadcast_loop(self):
        while True:
            msg = await self.global_queue.get()
            group = msg.get("group")
            data = msg.get("data")
            if not group or data is None:
                continue

            async with self.lock:
                clients = self.client_groups.get(group, set()).copy()

            disconnected: Set[WebSocket] = set()
            for client in clients:
                try:
                    await self._send_to_websocket(client, data)
                except Exception:
                    disconnected.add(client)

            if disconnected:
                async with self.lock:
                    for client in disconnected:
                        self.remove_client(client, group)

    def create_endpoint(self):
        async def endpoint(websocket: WebSocket, group: str = "default"):
            self.add_client(websocket, group)
            await self.event_generator(websocket, group)

        return endpoint

    async def producer(self):
        i = 0
        while True:
            await asyncio.sleep(10)
            i += 1
            await self.push_message({"group": "default", "data": {"message": f"A消息 {i}"}})


