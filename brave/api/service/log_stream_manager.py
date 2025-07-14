import asyncio
from typing import Dict, List, Callable, Coroutine, Optional
from fastapi import FastAPI, Request, Depends
from starlette.responses import StreamingResponse

app = FastAPI()
# 观察者模式（Observer Pattern）
# 你将每个日志源（Pod/Container）视为主题（Subject）

# 每个客户端连接（SSE）是一个观察者（Observer）

# 新用户只需注册订阅已有流，不再创建重复连接

# 优点：支持多个用户复用同一日志流


# --- LogStream 类 ---
class LogStream:
    def __init__(self, source_id: str, log_source: Callable[[], Coroutine]):
        self.source_id = source_id
        self.log_source_func = log_source
        self.subscribers: List[asyncio.Queue] = []
        self.task: Optional[asyncio.Task] = None
        self.running = False

    def subscribe(self) -> asyncio.Queue:
        q = asyncio.Queue()
        self.subscribers.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue):
        if q in self.subscribers:
            self.subscribers.remove(q)

    async def start(self):
        if self.running:
            return
        self.running = True

        async def stream_logs():
            try:
                async for line in self.log_source_func():
                    if not self.subscribers:
                        break
                    for q in list(self.subscribers):
                        await q.put(line)
            except Exception as e:
                print(f"Log stream error: {e}")
            finally:
                self.running = False

        self.task = asyncio.create_task(stream_logs())

    async def close(self):
        self.subscribers.clear()
        if self.task:
            self.task.cancel()
            self.task = None
        self.running = False


# --- 单例注册中心 ---
class LogStreamRegistry:
    def __init__(self):
        self.streams: Dict[str, LogStream] = {}

    def get_or_create(self, source_id: str, log_source: Callable[[], Coroutine]) -> LogStream:
        if source_id not in self.streams:
            self.streams[source_id] = LogStream(source_id, log_source)
        return self.streams[source_id]

    def remove(self, source_id: str):
        self.streams.pop(source_id, None)

log_registry = LogStreamRegistry()


# --- 模拟日志源（可替换为 docker/k8s 实现） ---
async def fake_log_generator():
    for i in range(100):
        await asyncio.sleep(0.5)
        yield f"log line {i}"


# --- SSE 接口 ---
@app.get("/logs/{source_id}")
async def stream_logs(request: Request, source_id: str):
    stream = log_registry.get_or_create(source_id, fake_log_generator)
    q = stream.subscribe()
    await stream.start()

    async def event_gen():
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    line = await asyncio.wait_for(q.get(), timeout=10)
                    yield f"data: {line}\n\n"
                except asyncio.TimeoutError:
                    yield ": keep-alive\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            stream.unsubscribe(q)

    return StreamingResponse(event_gen(), media_type="text/event-stream")


# --- 后台清理任务 ---
async def cleanup_task():
    while True:
        to_remove = []
        for sid, stream in log_registry.streams.items():
            if not stream.subscribers:
                await stream.close()
                to_remove.append(sid)
        for sid in to_remove:
            log_registry.remove(sid)
        await asyncio.sleep(30)

@app.on_event("startup")
async def start_cleanup():
    asyncio.create_task(cleanup_task())
