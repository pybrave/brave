from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import time
import queue
import threading
import asyncio

sseController = APIRouter()



# 全局生产者队列（数据源）
global_queue = asyncio.Queue()

# 所有客户端连接（用于广播）
connected_clients = set()

# 消费全局队列并广播给每个客户端
async def broadcast_loop():
    while True:
        msg = await global_queue.get()
        print(f"广播消息{msg} 客户端数量:{len(connected_clients)}")
        # 广播给所有客户端
        for q in connected_clients.copy():
            await q.put(msg)

# SSE 消息生成器，每个连接一个队列
async def event_generator(request: Request, client_queue: asyncio.Queue):
    try:
        while True:
            # print(f"is_disconnected: {request.is_disconnected()}")
            if await request.is_disconnected():
                print("请求关闭!")
                break
            try:
                msg = await asyncio.wait_for(client_queue.get(), timeout=10)
                print(f"产生消息{msg}!")
                yield f"data: {msg}\n\n"
            except asyncio.TimeoutError:
                yield ": keep-alive\n\n"
    except asyncio.CancelledError:
        print("连接被取消")
    finally:
        print("finally请求关闭!")
        connected_clients.discard(client_queue)

@sseController.get("/sse")
async def sse(request: Request):
    q = asyncio.Queue()
    connected_clients.add(q)
    return StreamingResponse(event_generator(request, q), media_type="text/event-stream")

@sseController.get("/send")
async def send_message(msg: str):
    await global_queue.put(msg)
    return {"status": "queued", "message": msg}



# 生产者示例：每隔5秒往队列里放一个数据
async def  producer():
    i = 1
    while True:
        await asyncio.sleep(10)
        print(f"📦 当前线程：{threading.current_thread().name}, 消息 {i}")
        await global_queue.put(f"消息 {i}")
        i += 1

# threading.Thread(target=producer, daemon=True).start()

