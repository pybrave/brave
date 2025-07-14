from fastapi import Request
from fastapi.responses import StreamingResponse
import asyncio

class SSEManager:
    def __init__(self, wq_manager):
        self.wq_manager = wq_manager

    def create_endpoint(self):
        async def endpoint(workflow_id: str, request: Request):
            queue = self.wq_manager.queues[workflow_id]

            async def event_generator():
                while True:
                    if await request.is_disconnected():
                        break
                    try:
                        msg = await asyncio.wait_for(queue.get(), timeout=10)
                        yield f"data: {msg}\n\n"
                    except asyncio.TimeoutError:
                        yield ": keep-alive\n\n"

            return StreamingResponse(event_generator(), media_type="text/event-stream")

        return endpoint

