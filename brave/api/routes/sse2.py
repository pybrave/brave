# 「消费全局队列并广播给每个客户端」 vs 「直接向所有客户端广播」

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import asyncio
from typing import Set

app = FastAPI()

# 所有活跃连接的队列
clients: Set[asyncio.Queue] = set()

# 发送广播给所有客户端
async def broadcast_message(message: str):
    for queue in clients.copy():
        await queue.put(message)

# 每个连接独立的 SSE 生成器
async def event_generator(request: Request, client_queue: asyncio.Queue):
    try:
        while True:
            # 客户端断开连接则退出
            if await request.is_disconnected():
                break
            try:
                # 等待消息
                message = await asyncio.wait_for(client_queue.get(), timeout=10)
                yield f"data: {message}\n\n"
            except asyncio.TimeoutError:
                # 心跳，防断开
                yield ": keep-alive\n\n"
    finally:
        # 连接断开，清除客户端队列
        clients.discard(client_queue)

@app.get("/sse")
async def sse(request: Request):
    # 为新客户端创建一个队列
    client_queue = asyncio.Queue()
    clients.add(client_queue)
    return StreamingResponse(event_generator(request, client_queue), media_type="text/event-stream")

@app.get("/send")
async def send_msg(msg: str):
    await broadcast_message(msg)
    return {"status": "sent", "message": msg}
