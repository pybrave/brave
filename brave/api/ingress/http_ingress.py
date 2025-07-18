from fastapi import Request, APIRouter
from brave.api.core.event import IngressEvent
from brave.api.core.routers.ingress_event_router import IngressEventRouter

class HTTPIngress:
    def __init__(self, router:IngressEventRouter):
        self.router = router

    def create_endpoint(self):
        async def endpoint(request: Request):
            msg = await request.json()
        
            evnet_str = msg.get("ingress_event")
            event = IngressEvent(evnet_str)
            if not event:
                event = IngressEvent.NEXTFLOW_EXECUTOR_EVENT
                print(f"[HTTP] Unknown event type '{event}'", msg)
                return
            data = msg.get("data")
            await self.router.dispatch(event,data)
            return {"status": "ok"}
        return endpoint
        # app.include_router(router)
