import asyncio
import json
from collections import defaultdict
from typing import Any, Dict, Optional, Set, Tuple

from fastapi import WebSocket, WebSocketDisconnect
from brave.api.service.realtime_service import RealtimeService


class WSSessionService(RealtimeService):
    """WebSocket service aligned with SSESessionService's public interface."""

    endpoint_transport = "websocket"

    def __init__(self):
        self.global_queue = asyncio.Queue()
        self.client_groups: Dict[str, Set[WebSocket]] = defaultdict(set)
        self.lock = asyncio.Lock()
        self.ack_timeout_seconds = 10
        self.ack_max_retries = 3
        self._seq_by_client: Dict[WebSocket, int] = defaultdict(int)
        self._pending_acks: Dict[WebSocket, Dict[int, Dict[str, Any]]] = defaultdict(dict)
        self._ack_lock = asyncio.Lock()

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
                    raw = await asyncio.wait_for(websocket.receive_text(), timeout=10)
                    await self._handle_client_message(websocket, raw)
                except asyncio.TimeoutError:
                    await self._retry_pending_acks(websocket)
                    await websocket.send_json({"type": "ping"})
        except WebSocketDisconnect:
            pass
        finally:
            await self._clear_client_state(websocket)
            async with self.lock:
                self.remove_client(websocket, group)

    async def push_message(self, msg: dict):
        # Message shape: {"group": "default", "data": ...}
        await self.global_queue.put(msg)

    async def push_message_default(self, msg: dict):
        # Keep same method as SSESessionService for compatibility.
        await self.global_queue.put({"group": "default", "data": msg})

    async def _next_seq(self, websocket: WebSocket) -> int:
        async with self._ack_lock:
            self._seq_by_client[websocket] += 1
            return self._seq_by_client[websocket]

    async def _mark_pending_ack(self, websocket: WebSocket, seq: int, payload: Dict[str, Any]):
        async with self._ack_lock:
            self._pending_acks[websocket][seq] = {
                "message": payload,
                "sent_at": asyncio.get_running_loop().time(),
                "retry_count": 0,
            }

    async def _ack_received(self, websocket: WebSocket, seq: int) -> bool:
        async with self._ack_lock:
            pending = self._pending_acks.get(websocket)
            if not pending:
                return False
            return pending.pop(seq, None) is not None

    async def _clear_client_state(self, websocket: WebSocket):
        async with self._ack_lock:
            self._seq_by_client.pop(websocket, None)
            self._pending_acks.pop(websocket, None)

    async def _retry_pending_acks(self, websocket: WebSocket):
        now = asyncio.get_running_loop().time()
        to_resend = []
        to_drop = []

        async with self._ack_lock:
            pending = self._pending_acks.get(websocket, {})
            for seq, meta in pending.items():
                if now - float(meta["sent_at"]) < self.ack_timeout_seconds:
                    continue
                if int(meta["retry_count"]) >= self.ack_max_retries:
                    to_drop.append(seq)
                    continue
                meta["retry_count"] = int(meta["retry_count"]) + 1
                meta["sent_at"] = now
                to_resend.append(dict(meta["message"]))
            for seq in to_drop:
                pending.pop(seq, None)

        for message in to_resend:
            await websocket.send_json(message)

    async def _handle_client_message(self, websocket: WebSocket, raw: str):
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return

        if not isinstance(data, dict):
            return

        if data.get("type") == "ack":
            seq = data.get("seq")
            if isinstance(seq, int):
                await self._ack_received(websocket, seq)
            return

        # ACK for client -> server messages with sequence.
        seq = data.get("seq")
        if isinstance(seq, int):
            await websocket.send_json({"type": "ack", "seq": seq})

    async def _prepare_payload_for_send(self, websocket: WebSocket, data: Any) -> Tuple[Any, Optional[int], bool]:
        if isinstance(data, dict):
            payload = dict(data)
            if payload.get("type") in {"ping", "ack"}:
                return payload, None, True
            requires_ack = bool(payload.get("require_ack", True))
            seq = payload.get("seq")
            if requires_ack:
                if not isinstance(seq, int):
                    seq = await self._next_seq(websocket)
                    payload["seq"] = seq
                payload["require_ack"] = True
                return payload, seq, True
            return payload, None, True

        if isinstance(data, str):
            try:
                parsed = json.loads(data)
                if isinstance(parsed, dict):
                    return await self._prepare_payload_for_send(websocket, parsed)
                return parsed, None, True
            except json.JSONDecodeError:
                return data, None, False

        if isinstance(data, list):
            return data, None, True

        return data, None, True

    async def _send_to_websocket(self, websocket: WebSocket, data: Any) -> Optional[int]:
        payload, seq, as_json = await self._prepare_payload_for_send(websocket, data)

        if as_json:
            await websocket.send_json(payload)
        else:
            await websocket.send_text(payload)

        if seq is not None and isinstance(payload, dict):
            await self._mark_pending_ack(websocket, seq, payload)

        return seq

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


