from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import time
import queue
import threading
sseController = APIRouter()


# 创建线程安全的队列
event_queue = queue.Queue()

# SSE 推送生成器
def event_generator():
    while True:
        try:
            # 阻塞等待新数据（最多等待1秒，避免无法关闭）
            data = event_queue.get(timeout=1)
            print(data)
            yield f"data: {data}\n\n"
        except queue.Empty:
            # 没有数据就继续等待
            continue


@sseController.get("/sse")
async def sse(request: Request):
    return StreamingResponse(event_generator(), media_type="text/event-stream")


# 生产者示例：每隔5秒往队列里放一个数据
def producer():
    i = 1
    while True:
        time.sleep(5)
        event_queue.put(f"消息 {i}")
        i += 1

# 启动生产线程
# threading.Thread(target=producer, daemon=True).start()