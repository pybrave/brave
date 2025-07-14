import os
import asyncio
import socket
import json
from .event_router import EventRouter

class UDSListener:
    def __init__(self, uds_path: str, router: EventRouter):
        self.uds_path = uds_path
        self.router = router

    async def start(self):
        if os.path.exists(self.uds_path):
            os.remove(self.uds_path)

        server = await asyncio.start_unix_server(self.handle_client, path=self.uds_path)
        print(f"[UDS] Listening at {self.uds_path}")
        async with server:
            await server.serve_forever()

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        try:
            while line := await reader.readline():
                try:
                    msg = json.loads(line.decode().strip())
                    await self.router.dispatch(msg)
                except Exception as e:
                    print(f"[UDS] Message error: {e}")
        except Exception as e:
            print(f"[UDS] Client error: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

# class UDSListener:
#     def __init__(self, uds_path: str, wq_manager: WorkflowQueueManager):
#         self.uds_path = uds_path
#         self.wq_manager = wq_manager

#     async def start(self):
#         if os.path.exists(self.uds_path):
#             os.remove(self.uds_path)

#         server = await asyncio.start_unix_server(self.handle_client, path=self.uds_path)
#         print(f"[UDS] Listening at {self.uds_path}")
#         async with server:
#             await server.serve_forever()

#     async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
#         try:
#             while line := await reader.readline():
#                 try:
#                     msg = json.loads(line.decode().strip())
#                     workflow_id = msg.get("workflow_id", "global")
#                     await self.wq_manager.put(workflow_id, msg)
#                 except Exception as e:
#                     print(f"[UDS] Message error: {e}")
#         except Exception as e:
#             print(f"[UDS] Client error: {e}")
#         finally:
#             writer.close()
#             await writer.wait_closed()
