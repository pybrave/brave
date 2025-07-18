from fastapi import Request
from fastapi.responses import StreamingResponse
import asyncio
from brave.api.core.workflow_queue import WorkflowQueueManager
class WorkflowSSEManager:
    def __init__(self, workflow_queue_manager: WorkflowQueueManager):
        self.workflow_queue_manager = workflow_queue_manager
    def create_endpoint(self):
        async def endpoint(workflow_id: str, request: Request):
            queue = asyncio.Queue()

            # 订阅 pubsub，收到新消息后放入本地队列
            def subscriber(msg):
                queue.put_nowait(msg)

            self.workflow_queue_manager.register_subscriber(workflow_id, subscriber)

            async def event_generator():
                try:
                    while True:
                        if await request.is_disconnected():
                            break
                        try:
                            msg = await asyncio.wait_for(queue.get(), timeout=10)
                            yield f"data: {msg}\n\n"
                        except asyncio.TimeoutError:
                            yield ": keep-alive\n\n"
                finally:
                    # 取消订阅
                    self.workflow_queue_manager.pubsub.unsubscribe(workflow_id, subscriber)

            return StreamingResponse(event_generator(), media_type="text/event-stream")

        return endpoint
    # def create_endpoint(self):
    #     async def endpoint(workflow_id: str, request: Request):
    #         queue = self.workflow_queue_manager.get(workflow_id)

    #         async def event_generator():
    #             while True:
    #                 if await request.is_disconnected():
    #                     break
    #                 try:
    #                     msg = await asyncio.wait_for(queue.queue.get(), timeout=10)
    #                     yield f"data: {msg}\n\n"
    #                 except asyncio.TimeoutError:
    #                     yield ": keep-alive\n\n"

    #         return StreamingResponse(event_generator(), media_type="text/event-stream")

    #     return endpoint




