from typing import Callable, Awaitable, Dict, Union, Coroutine
import asyncio
from collections import defaultdict
from brave.api.core.base_event_router import BaseEventRouter
from brave.api.core.event import WorkflowEvent
from brave.api.schemas.analysis import Analysis
from brave.api.service import analysis_service
from brave.api.config.db import get_engine

Callback = Union[Callable[[Analysis,dict], None],Callable[[Analysis,dict], Coroutine]]

class WorkflowEventRouter(BaseEventRouter[WorkflowEvent,Callback]):
    def __init__(self):
        super().__init__()
        self._analysis_cache: dict[str, Analysis] = {}

    def invalidate_cache(self, analysis_id: str):
        """清除缓存"""
        self._analysis_cache.pop(analysis_id, None)

    async def get_analysis(self, analysis_id: str) -> Analysis:
        if analysis_id not in self._analysis_cache:
            with get_engine().begin() as conn:
                analysis =  analysis_service.find_analysis_by_id(conn,analysis_id)
                if analysis is None:
                    raise ValueError(f"Analysis with id {analysis_id} not found")
                analysis_dict = dict(analysis)  # Convert Row to dict if needed
                analysis = Analysis(**analysis_dict)
                self._analysis_cache[analysis_id] = analysis
        return self._analysis_cache[analysis_id]

    async def dispatch(self,event:WorkflowEvent, analysis_id:str,msg: dict):
        # event = msg.get("workflow_event")
        # if not event:
        #     print("[EventRouter] No 'workflow_event' in message", msg)
        #     return
        analysis = await self.get_analysis(analysis_id)
        handlers = self._handlers.get(event)
        if handlers:
            for handler in handlers:
                if asyncio.iscoroutinefunction(handler):
                    await handler(analysis,msg)
                else:
                    handler(analysis,msg)
        else:
            print(f"[WorkflowEventRouter] No handler for event '{event}'")

        if event == WorkflowEvent.ON_FLOW_COMPLETE:
            self.invalidate_cache(analysis_id)

# @lru_cache(maxsize=1)
# def get_router():
#     return WorkflowEventRouter()