from fastapi import APIRouter, Request, HTTPException,Depends   
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from brave.api.service.sse_service import SSESessionService
import json
from dependency_injector.wiring import inject, Provide
from brave.app_container import AppContainer
sseController = APIRouter()



# # 全局生产者队列（数据源）
# global_queue = asyncio.Queue()

# # 所有客户端连接（用于广播）
# connected_clients = set()

# # 消费全局队列并广播给每个客户端
# async def broadcast_loop():
#     current_loop = asyncio.get_event_loop()
#     print(f"broadcast_loop 事件循环：{current_loop}")
#     while True:
#         msg = await global_queue.get()
#         print(f"广播消息{msg} 客户端数量:{len(connected_clients)}")
#         # 广播给所有客户端
#         for q in connected_clients.copy():
#             await q.put(msg)

# # SSE 消息生成器，每个连接一个队列
# async def event_generator(request: Request, client_queue: asyncio.Queue):
#     try:
#         while True:
#             # print(f"is_disconnected: {request.is_disconnected()}")
#             if await request.is_disconnected():
#                 print("请求关闭!")
#                 break
#             try:
#                 msg = await asyncio.wait_for(client_queue.get(), timeout=10)
#                 print(f"产生消息{msg}!")
#                 yield f"data: {msg}\n\n"
#             except asyncio.TimeoutError:
#                 yield ": keep-alive\n\n"
#     except asyncio.CancelledError:
#         print("连接被取消")
#     finally:
#         print("finally请求关闭!")
#         connected_clients.discard(client_queue)

# @sseController.get("/sse")
# async def sse(request: Request):
#     q = asyncio.Queue()
#     connected_clients.add(q)
#     return StreamingResponse(event_generator(request, q), media_type="text/event-stream")

# @sseController.get("/send")
# async def send_message(msg: str):
#     await global_queue.put(msg)
#     return {"status": "queued", "message": msg}




# # 生产者示例：每隔5秒往队列里放一个数据
# async def  producer():
#     i = 1
#     while True:
#         await asyncio.sleep(10)
#         print(f"📦 当前线程：{threading.current_thread().name}, 消息 {i}")
#         await global_queue.put(f"消息 {i}")
#         i += 1

# threading.Thread(target=producer, daemon=True).start()

# from brave.api.service.sse_service import sse_service  # 从 service.py 导入


# @sseController.get("/sse")
# async def sse(request: Request):
#     q = asyncio.Queue()
#     sse_service = request.app.state.sse_service  # 从 app.state 获取实例
#     sse_service.add_client(q)
#     return StreamingResponse(sse_service.event_generator(request, q), media_type="text/event-stream")


# @sseController.get("/sse-group")
# async def sse_group(request: Request,group="default"):
#     q = asyncio.Queue()
#     manager: AppManager = request.app.state.manager  # 从 app.state 获取实例
#     if manager.sse_service is None:
#         raise HTTPException(status_code=500, detail="SSE服务未初始化")
        
#     manager.sse_service.add_client(q,group)
#     return StreamingResponse(manager.sse_service.event_generator(request, q,group), media_type="text/event-stream")


# @sseController.get("/send")
# async def send_message(msg: str, request: Request):
#     manager: AppManager = request.app.state.manager  # 从 app.state 获取实例
#     if manager.sse_service is None:
#         raise HTTPException(status_code=500, detail="SSE服务未初始化")
#     await manager.sse_service.push_message({"group":"default","data":msg})
#     return {"status": "queued", "message": msg}

@sseController.get("/send-test")
@inject
async def send_message2(sse_service:SSESessionService = Depends(Provide[AppContainer.realtime_service])  ):
    data = {"msgType":"test","msg":"hello"}
    data ={
        "action": "router.go",
        "payload": {
            "path": "/c/scripts",
        }
    }
    data = {
        "actions":[
            {
                "action": "router.go",
                "payload": {
                    "path": "/c/tools",
                    "state": {"last":True}
                }
            },{
                "action": "component.invoke",
                "payload": {
                    "category": "tables",
                    "id": "tools-card",
                    "method": "reload"
                }
            }, {"action": "ui.show_message", "payload": {"type": "success", "text": "工具创建成功"}}
        ]
    }
    data = {
        "action": "component.invoke",
        "payload": {
            "category": "analysis",
            "id": "params-form",
            "method": "updateFormStatus",
            "args": {
                "status": "done"
            }
        }
    }
    await sse_service.push_message({"group":"default",
                                    "data":json.dumps(data)})
    return {"message": "success"}