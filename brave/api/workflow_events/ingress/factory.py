from .uds_stream import UDSStreamIngress
from .uds_socket import UDSSocketIngress
from .http_ingress import HTTPIngress


def create_ingress(mode, path, router):
    if mode == "stream":
        return UDSStreamIngress(path, router)
    elif mode == "socket":
        return UDSSocketIngress(path, router)
    elif mode == "http":
        return HTTPIngress(router)
    else:
        raise ValueError(f"Unsupported ingress mode: {mode}")