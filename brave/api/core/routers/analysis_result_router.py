from typing import Callable, Awaitable, Dict, Union, Coroutine
import asyncio
from collections import defaultdict

from brave.api.core.base_event_router import BaseEventRouter
from brave.api.core.event import AnalysisResultEvent
from brave.api.schemas.analysis import Analysis, AnalysisExecuterModal
from brave.api.schemas.analysis_result import AnalysisResult, AnalysisResultParseModal

Callback = Union[Callable[[Analysis,AnalysisResultParseModal], None], Callable[[Analysis,AnalysisResultParseModal], Coroutine]]

class AnalysisResultRouter(BaseEventRouter[AnalysisResultEvent,Callback]):
    async def dispatch(self, event: AnalysisResultEvent, analsyis: Analysis,analysis_result:AnalysisResultParseModal):
        handlers = self._handlers.get(event, [])
 
        for handler in handlers:
            if asyncio.iscoroutinefunction(handler):
                await handler(analsyis,analysis_result )
            else:
                handler(analsyis,analysis_result)

    