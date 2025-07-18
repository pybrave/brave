import os
import asyncio
import json
from .interfaces.base_ingress import BaseMessageIngress
from brave.api.core.routers.ingress_event_router import IngressEventRouter
from brave.api.core.event import IngressEvent
class UDSStreamIngress(BaseMessageIngress):
    def __init__(self, path, router:IngressEventRouter):
        self.path = path
        self.router = router

    async def start(self):
        if os.path.exists(self.path):
            os.remove(self.path)
        server = await asyncio.start_unix_server(self._handle, path=self.path)
        print(f"[UDS-STREAM] Listening at {self.path}")
        async with server:
            await server.serve_forever()

    async def _handle(self, reader, writer):
        try:
            while line := await reader.readline():
                try:
                    msg = json.loads(line.decode().strip())
                    
                    evnet_str = msg.get("ingress_event")
                    event = IngressEvent(evnet_str)
                    if not event:
                        event = IngressEvent.NEXTFLOW_EXECUTOR_EVENT
                        print(f"[UDS-STREAM] Unknown event type '{event}'", msg)
                        return
                    data = msg.get("data")
                    await self.router.dispatch(event,data)
                except Exception as e:
                    print(f"[UDS-STREAM] Message error: {e}")
        except Exception as e:
            print(f"[UDS-STREAM] Client error: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
