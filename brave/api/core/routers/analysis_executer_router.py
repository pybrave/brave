from typing import Callable, Awaitable, Dict, Union, Coroutine
import asyncio
from collections import defaultdict

from pydantic import BaseModel

from brave.api.core.base_event_router import BaseEventRouter
from brave.api.core.event import AnalysisExecutorEvent
from brave.api.schemas.analysis import AnalysisExecuterModal, AnalysisId
import brave.api.service.analysis_service as analysis_service
from brave.api.config.db import get_engine

Callback = Union[Callable[[AnalysisExecuterModal], None], Callable[[AnalysisExecuterModal], Coroutine]]

class AnalysisExecutorRouter(BaseEventRouter[AnalysisExecutorEvent,Callback]):
    async def dispatch(self, event: AnalysisExecutorEvent, payload: BaseModel):
        handlers = self._handlers.get(event, [])
        # expected_type = self._payload_types.get(event)
        # if  expected_type:
        #     if not isinstance(payload, expected_type):
        #         raise TypeError(f"[EventRouter] Expected payload type {expected_type}, got {type(payload)}")

        if event == AnalysisExecutorEvent.ON_ANALYSIS_COMPLETE or event == AnalysisExecutorEvent.ON_ANALYSIS_FAILED:    
            if isinstance(payload, AnalysisId):
                with get_engine().begin() as conn:
                    analysis =  analysis_service.find_analysis_by_id(conn,payload.analysis_id)
                    if analysis:
                        payload = AnalysisExecuterModal(**analysis)
                # payload = AnalysisExecuterModal(analysis_id=payload.analysis_id)

        if not isinstance(payload, AnalysisExecuterModal):
            raise TypeError(f"[EventRouter] Expected payload type {AnalysisExecuterModal}, got {type(payload)}")
        if handlers:
            for handler in handlers:
                if asyncio.iscoroutinefunction(handler):
                    await handler(payload)
                else:
                    handler(payload)
        else:
            print(f"[AnalysisExecutorRouter] No handler for event '{event}'")
            
    
    # async def dispatch(self,event:AnalysisExecutorEvent, analysis_id:str,msg: dict):
    #     # event = msg.get("workflow_event")
    #     # if not event:
    #     #     print("[EventRouter] No 'workflow_event' in message", msg)
    #     #     return
    #     handlers = self._handlers.get(event)
    #     if handlers:
    #         for handler in handlers:
    #             if asyncio.iscoroutinefunction(handler):
    #                 await handler(analysis_id,msg)
    #             else:
    #                 handler(analysis_id,msg)
    #     else:
    #         print(f"[EventRouter] No handler for event '{event}'")
    # # def __init__(self):
    #     self._handlers: dict[WatchFileEvent, set[Callback]] = defaultdict(set)

    # def on_event(self, event: WatchFileEvent):
    #     def decorator(func: Callback):
    #         self._handlers[event].add(func)
    #         return func
    #     return decorator

    # def register_handler(self, event: WatchFileEvent, handler: Callback):
    #     self._handlers[event].add(handler)


    # async def dispatch(self, event:WatchFileEvent,msg: dict):
    #     # event = msg.get("file_type")
    #     # if not event:
    #     #     print("[WatchFileEvenetRouter] No 'file_type' in message", msg)
    #     #     return
    #     handlers = self._handlers.get(event)
    #     if handlers:
    #         for handler in handlers:
    #             if asyncio.iscoroutinefunction(handler):
    #                 await handler(msg)
    #             else:
    #                 handler(msg)
    #     else:
    #         print(f"[WatchFileEvenetRouter] No handler for event '{event}'")

