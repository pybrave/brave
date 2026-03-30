import asyncio
import json
from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

ws_app = APIRouter()
    

def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_action_messages(start_seq: int = 1) -> List[Dict[str, Any]]:
    """Build a repeatable demo action stream for frontend ActionDispatcher."""
    seq = start_seq
    messages: List[Dict[str, Any]] = [
        {
            "seq": seq,
            "type": "action",
            "action": "ui.show_message",
            "payload": {"type": "success", "text": "WebSocket connected"},
            "ts": _utc_now_iso(),
        },
        {
            "seq": seq + 1,
            "type": "action",
            "action": "ui.show_notification",
            "payload": {
                "type": "info",
                "message": "Task started",
                "description": "Demo stream is running",
            },
            "ts": _utc_now_iso(),
        },
        {
            "seq": seq + 2,
            "type": "action",
            "action": "router.go",
            "payload": {"path": "/c/scripts"},
            "ts": _utc_now_iso(),
        },
        {
            "seq": seq + 3,
            "type": "action",
            "action": "ui.show_message",
            "payload": {"type": "warning", "text": "High latency detected"},
            "ts": _utc_now_iso(),
        },{
            "seq": seq + 4,
            "type": "action",
            "action": "router.go",
            "payload": {"path": "/c/tools"},
            "ts": _utc_now_iso(),
        },
    ]
    return messages




# @ws_app.websocket("/ws-group")
async def mock_actions(websocket: WebSocket) -> None:
    await websocket.accept()
    print("[ws] client connected")

    seq_base = 1
    stop_event = asyncio.Event()

    async def sender() -> None:
        nonlocal seq_base
        while not stop_event.is_set():
            action_messages = build_action_messages(start_seq=seq_base)
            for message in action_messages:
                if stop_event.is_set():
                    return
                await websocket.send_json(message)
                await asyncio.sleep(2)
            seq_base += len(action_messages)

    async def heartbeat() -> None:
        while not stop_event.is_set():
            await asyncio.sleep(5)
            if stop_event.is_set():
                return
            await websocket.send_json({"type": "ping", "ts": _utc_now_iso()})

    async def receiver() -> None:
        while not stop_event.is_set():
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                print(f"[ws] non-json message: {raw}")
                continue

            if data.get("type") == "ack":
                print(f"[ws] ack received: seq={data.get('seq')}")
            else:
                print(f"[ws] client message: {data}")

    sender_task = asyncio.create_task(sender())
    heartbeat_task = asyncio.create_task(heartbeat())
    receiver_task = asyncio.create_task(receiver())

    try:
        await receiver_task
    except WebSocketDisconnect:
        print("[ws] client disconnected")
    finally:
        stop_event.set()
        for task in (sender_task, heartbeat_task, receiver_task):
            task.cancel()
        await asyncio.gather(sender_task, heartbeat_task, receiver_task, return_exceptions=True)


