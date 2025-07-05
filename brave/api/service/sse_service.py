# service.py

import asyncio
import threading

class SSEService:
    def __init__(self):
        self.global_queue = asyncio.Queue()
        self.connected_clients = set()

    async def broadcast_loop(self):
        current_loop = asyncio.get_event_loop()
        print(f"broadcast_loop 事件循环：{current_loop}")
        while True:
            msg = await self.global_queue.get()
            print(f"广播消息: {msg} 客户端数量: {len(self.connected_clients)}")
            for q in self.connected_clients.copy():
                await q.put(msg)

    async def event_generator(self, request, client_queue):
        try:
            while True:
                if await request.is_disconnected():
                    print("请求关闭!")
                    break
                try:
                    msg = await asyncio.wait_for(client_queue.get(), timeout=10)
                    print(f"产生消息: {msg}!")
                    yield f"data: {msg}\n\n"
                except asyncio.TimeoutError:
                    yield ": keep-alive\n\n"
        except asyncio.CancelledError:
            print("连接被取消")
        finally:
            print("finally请求关闭!")
            self.connected_clients.discard(client_queue)

    async def push_message(self, msg: str):
        await self.global_queue.put(msg)

    def add_client(self, client_queue):
        self.connected_clients.add(client_queue)

    def remove_client(self, client_queue):
        self.connected_clients.discard(client_queue)

    async def producer(self):
        i = 1
        while True:
            await asyncio.sleep(10)
            print(f"📦 当前线程：{threading.current_thread().name}, 消息 {i}")
            await self.push_message(f"消息 {i}")
            i += 1



sse_service = SSEService()