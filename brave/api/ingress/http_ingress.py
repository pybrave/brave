from fastapi import Request, APIRouter
from brave.api.core.ingress_event_router import IngressEventRouter

class HTTPIngress:
    def __init__(self, router:IngressEventRouter):
        self.router = router

    def register(self, app):
        router = APIRouter()

        @router.post("/event/push")
        async def push_event(request: Request):
            data = await request.json()
            await self.router.dispatch(data)
            return {"status": "ok"}

        app.include_router(router)
