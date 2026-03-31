
import json
from typing import Any, Dict, List, Tuple

from brave.app_container import AppContainer


_ALLOWED_ACTIONS = {
    "ui.show_message",
    "ui.show_notification",
    "component.invoke",
    "router.go",
    "form.set_value",
    "form.reset",
}


def _normalize_actions(arguments: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], str]:
    # Backward-compatible: accept either single action+payload or actions[] batch.
    if isinstance(arguments.get("actions"), list):
        normalized: List[Dict[str, Any]] = []
        for item in arguments["actions"]:
            if not isinstance(item, dict):
                continue
            action = item.get("action")
            payload = item.get("payload", {})
            if isinstance(action, str):
                normalized.append({"action": action, "payload": payload})
        if not normalized:
            return [], "参数 actions 为空或格式不正确"
        return normalized, ""

    action = arguments.get("action")
    payload = arguments.get("payload", {})
    if not isinstance(action, str):
        return [], "缺少参数 action"
    return [{"action": action, "payload": payload}], ""


async def ui_action(arguments: dict, sse_service=None):
    if sse_service is None:
        # Reuse runtime-configured realtime implementation (SSE or WebSocket).
        sse_service = AppContainer.realtime_service()

    actions, err = _normalize_actions(arguments)
    if err:
        return err

    invalid = [item["action"] for item in actions if item["action"] not in _ALLOWED_ACTIONS]
    if invalid:
        return f"不支持的 action: {', '.join(invalid)}"

    pushed = 0
    for item in actions:
        payload = item.get("payload")
        if not isinstance(payload, dict):
            payload = {}

        message = {
            "type": "action",
            "action": item["action"],
            "payload": payload,
        }
        await sse_service.push_message({"group": "default", "data": json.dumps(message, ensure_ascii=False)})
        pushed += 1

    if pushed == 1:
        return f"已发送 UI 指令: {actions[0]['action']}"
    return f"已发送 {pushed} 条 UI 指令"
