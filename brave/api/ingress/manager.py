# brave/api/ingress/manager.py
from fastapi import FastAPI
from .factory import  create_ingress, IngressMode
from .interfaces.base_ingress import BaseMessageIngress
from brave.api.core.routers.ingress_event_router import IngressEventRouter
from .http_ingress import HTTPIngress

class IngressManager:
    def __init__(
        self, 
        ingress_event_router: IngressEventRouter ,
        event_mode: IngressMode = IngressMode.STREAM, 
        uds_path: str = "/tmp/brave.sock"):
    
        # self.ingress: BaseMessageIngress = create_ingress(event_mode, uds_path, ingress_event_router)
        self.ingress = create_ingress(event_mode, uds_path, ingress_event_router)

    async def start(self):
        if isinstance(self.ingress, BaseMessageIngress):
            await self.ingress.start()
    
    def create_endpoint(self):
        if isinstance(self.ingress, HTTPIngress):
            return self.ingress.create_endpoint()
        return None

    # def register_http(self, app):
    #     if isinstance(self.ingress, HTTPIngress):
    #         self.ingress.register(app)
