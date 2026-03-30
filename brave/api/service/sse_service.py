# service.py

import asyncio
import threading
from collections import defaultdict
from functools import lru_cache
from typing import Dict, Set
import json
from fastapi import Request
from fastapi.responses import StreamingResponse
from brave.api.service.realtime_service import RealtimeService


# class SSEService:
#     def __init__(self):
#         self.global_queue = asyncio.Queue()
#         self.connected_clients = set()

#     async def broadcast_loop(self):
#         # current_loop = asyncio.get_event_loop()
#         # print(f"broadcast_loop 事件循环：{current_loop}")
#         while True:
#             msg = await self.global_queue.get()
#             print(f"广播消息: {msg} 客户端数量: {len(self.connected_clients)}")
#             for q in self.connected_clients.copy():
#                 await q.put(msg)

#     async def event_generator(self, request, client_queue):
#         try:
#             # 首条立即推送，确保客户端立即建立连接
#             # yield "data: connected\n\n"
#             while True:
#                 if await request.is_disconnected():
#                     print("请求关闭!")
#                     break
#                 try:
#                     msg = await asyncio.wait_for(client_queue.get(), timeout=10)
#                     print(f"产生消息: {msg}!")
#                     yield f"data: {msg}\n\n"
#                 except asyncio.TimeoutError:
#                     yield ": keep-alive\n\n"
#         except asyncio.CancelledError:
#             print("连接被取消")
#         finally:
#             print("finally请求关闭!")
#             self.connected_clients.discard(client_queue)

#     async def push_message(self, msg: str):
#         await self.global_queue.put(msg)

#     def add_client(self, client_queue):
#         self.connected_clients.add(client_queue)

#     def remove_client(self, client_queue):
#         self.connected_clients.discard(client_queue)

#     def create_endpoint(self):
#         async def endpoint(request: Request):
#             q = asyncio.Queue()
#             self.add_client(q)
#             return StreamingResponse(self.event_generator(request, q), media_type="text/event-stream")
#         return endpoint

#     async def producer(self):
#         i = 1
#         while True:
#             await asyncio.sleep(10)
#             print(f"📦 当前线程：{threading.current_thread().name}, 消息 {i}")
#             await self.push_message(f"消息 {i}")
#             i += 1





class SSESessionService(RealtimeService):
    endpoint_transport = "http"

    def __init__(self):
        self.global_queue = asyncio.Queue()
        self.client_groups: Dict[str, Set[asyncio.Queue]] = defaultdict(set)
        self.lock = asyncio.Lock()

    def add_client(self, client_queue: asyncio.Queue, group: str):
        self.client_groups[group].add(client_queue)

    def remove_client(self, client_queue: asyncio.Queue, group: str):
        self.client_groups[group].discard(client_queue)

    async def event_generator(self, request, client_queue: asyncio.Queue, group: str):
        yield ": keep-alive\n\n"
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    msg = await asyncio.wait_for(client_queue.get(), timeout=10)
                    yield f"data: {msg}\n\n"
                except asyncio.TimeoutError:
                    # yield ": keep-alive\n\n"
                    yield f"data: {json.dumps({'type': 'ping'})}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            async with self.lock:
                self.remove_client(client_queue, group)

    async def push_message(self, msg: dict):
        # 消息结构：{"group": "typeA", "data": "hello"}
        await self.global_queue.put(msg)

    async def push_message_default(self, msg: dict):
        # 消息结构：{"group": "typeA", "data": "hello"}
        await self.global_queue.put({"group": "default", "data": msg})

    async def broadcast_loop(self):
        while True:
            msg = await self.global_queue.get()
            group = msg.get("group")
            data = msg.get("data")
            if not group or data is None:
                continue  # 忽略非法消息
            async with self.lock:
                clients = self.client_groups.get(group, set()).copy()
            print(f"📣 广播到组 {group}: {data}, 客户端数量: {len(clients)}")
            for q in clients:
                await q.put(data)
    def create_endpoint(self):
        async def endpoint(request: Request, group: str = "default"):
            q = asyncio.Queue()
            self.add_client(q, group)
            return StreamingResponse(self.event_generator(request, q, group), media_type="text/event-stream")
        return endpoint

    async def producer(self):
        i = 0
        while True:
            await asyncio.sleep(10)
            i += 1
            msgA = {"group": "default", "data": f"A消息 {i}"}
            # msgB = {"group": "typeB", "data": f"B消息 {i}"}
            await self.push_message(msgA)
            # await self.push_message(msgB)


# @lru_cache()
# def get_sse_service():
#     sse_service = SSESessionService()
#     return sse_service

# from collections import defaultdict
# from typing import Dict, Set
# import asyncio
# import threading

# class SSEService:
#     def __init__(self):
#         # 改为多个 group 队列，每个 group 的 queue 是多个 client queue
#         self.client_groups: Dict[str, Set[asyncio.Queue]] = defaultdict(set)
#         self.lock = asyncio.Lock()

#     async def event_generator(self, request, client_queue, group: str):
#         try:
#             while True:
#                 if await request.is_disconnected():
#                     print(f"请求关闭! 组: {group}")
#                     break
#                 try:
#                     msg = await asyncio.wait_for(client_queue.get(), timeout=10)
#                     yield f"data: {msg}\n\n"
#                 except asyncio.TimeoutError:
#                     yield ": keep-alive\n\n"
#         except asyncio.CancelledError:
#             print("连接被取消")
#         finally:
#             print(f"finally 请求关闭! 组: {group}")
#             async with self.lock:
#                 self.client_groups[group].discard(client_queue)

#     async def push_message(self, msg: str, group: str):
#         async with self.lock:
#             queues = self.client_groups.get(group, set()).copy()
#         print(f"📢 向组 [{group}] 发送消息 {msg}，客户端数量: {len(queues)}")
#         for q in queues:
#             await q.put(msg)

#     def add_client(self, client_queue: asyncio.Queue, group: str):
#         self.client_groups[group].add(client_queue)

#     def remove_client(self, client_queue: asyncio.Queue, group: str):
#         self.client_groups[group].discard(client_queue)


# from fastapi import Request
# from fastapi.responses import StreamingResponse
# from fastapi import APIRouter

# sseController = APIRouter()

# @sseController.get("/sse")
# async def sse(request: Request, group: str = "default"):
#     q = asyncio.Queue()
#     sse_service = request.app.state.sse_service
#     sse_service.add_client(q, group)
#     return StreamingResponse(sse_service.event_generator(request, q, group), media_type="text/event-stream")
