import os
import asyncio
import socket
import json
from brave.api.core.ingress_event_router import IngressEventRouter
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
                    await self.router.dispatch(msg)
                except Exception as e:
                    print(f"[UDS-SOCKET] Error: {e}")
                    break