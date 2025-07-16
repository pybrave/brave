from .uds_stream import UDSStreamIngress
from .uds_socket import UDSSocketIngress
from .http_ingress import HTTPIngress
from brave.api.core.ingress_event_router import IngressEventRouter

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

def create_ingress(mode, path, router:IngressEventRouter):
    if mode == "stream":
        return UDSStreamIngress(path, router)
    elif mode == "socket":
        return UDSSocketIngress(path, router)
    elif mode == "http":
        return HTTPIngress(router)
    else:
        raise ValueError(f"Unsupported ingress mode: {mode}")