from fastapi import Request, APIRouter

class HTTPIngress:
    def __init__(self, router):
        self.router = router

    def register(self, app):
        router = APIRouter()

        @router.post("/event/push")
        async def push_event(request: Request):
            data = await request.json()
            await self.router.dispatch(data)
            return {"status": "ok"}

        app.include_router(router)
