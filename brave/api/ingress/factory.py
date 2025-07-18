from .uds_stream import UDSStreamIngress
from .uds_socket import UDSSocketIngress
from .http_ingress import HTTPIngress
from brave.api.core.routers.ingress_event_router import IngressEventRouter

# brave/api/core/ingress_factory.py
# class IngressFactory:
#     def __init__(self, event_mode: str, uds_path: str,ingress_event_router: IngressEventRouter):
#         self.event_mode = event_mode
#         self.uds_path = uds_path
#         self.ingress_event_router = ingress_event_router
        
#     def create(self):
#         if self.event_mode == "stream":
#             return UDSStreamIngress(self.uds_path, self.ingress_event_router)
#         elif self.event_mode == "socket":
#             return UDSSocketIngress(self.uds_path, self.ingress_event_router)
#         elif self.event_mode == "http":
#             return HTTPIngress(self.ingress_event_router)
#         else:
#             raise ValueError(f"Unsupported ingress mode: {self.event_mode}")

from enum import Enum

class IngressMode(Enum):
    STREAM = "stream"
    SOCKET = "socket"
    HTTP = "http"

def create_ingress(mode: IngressMode, path, router: IngressEventRouter):
    if mode == IngressMode.STREAM:
        return UDSStreamIngress(path, router)
    elif mode == IngressMode.SOCKET:
        return UDSSocketIngress(path, router)
    elif mode == IngressMode.HTTP:
        return HTTPIngress(router)
    else:
        raise ValueError(f"Unsupported ingress mode: {mode}")