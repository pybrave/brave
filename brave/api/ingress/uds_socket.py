import os
import asyncio
import socket
import json
from brave.api.core.event import IngressEvent
from brave.api.core.routers.ingress_event_router import IngressEventRouter
from .interfaces.base_ingress import BaseMessageIngress

class UDSSocketIngress(BaseMessageIngress):
    def __init__(self, path, router:IngressEventRouter):
        self.path = path
        self.router = router

    async def start(self):
        if os.path.exists(self.path):
            os.remove(self.path)
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.bind(self.path)
        sock.listen(100)
        sock.setblocking(False)
        print(f"[UDS-SOCKET] Listening at {self.path}")
        loop = asyncio.get_running_loop()
        while True:
            client, _ = await loop.sock_accept(sock)
            asyncio.create_task(self._handle(client))

    async def _handle(self, client):
        loop = asyncio.get_running_loop()
        with client:
            while True:
                try:
                    data = await loop.sock_recv(client, 4096)
                    if not data:
                        break
                    msg = json.loads(data.decode())
                    evnet_str = msg.get("ingress_event")
                    event = IngressEvent(evnet_str)
                    if not event:
                        event = IngressEvent.NEXTFLOW_EXECUTOR_EVENT
                        print(f"[UDS-SOCKET] Unknown event type '{event}'", msg)
                        return
                    data = msg.get("data")
                    await self.router.dispatch(event,data)
                except Exception as e:
                    print(f"[UDS-SOCKET] Error: {e}")
                    break