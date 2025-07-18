from typing import Type, TypeVar
from brave.api.core.base_event_router import BaseEventRouter
from brave.api.core.routers_name import RoutersName

T = TypeVar("T", bound=BaseEventRouter)

class EventBus:
    def __init__(self):
        self.routers: dict[RoutersName, BaseEventRouter] = {}

    def register_router(self, name: RoutersName, router: BaseEventRouter):
        self.routers[name] = router

    async def dispatch(self, router_name: RoutersName, event_type:Type[T], payload: dict):
        router = self.routers.get(router_name)
        if router:
            await router.dispatch(event_type, payload)
        else:
            print(f"[EventBus] No router found for '{router_name}'")
