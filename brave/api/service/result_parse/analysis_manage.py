
from collections import defaultdict

from pydantic import BaseModel
from brave.api.config.db import get_engine
from brave.api.core.evenet_bus import EventBus


from .result_parse import ResultParse


class AnalysisManage:
    def __init__(
        self,
        event_bus:EventBus) -> None:
        self._result_parse: dict[str, ResultParse] = defaultdict()
        self.event_bus = event_bus
    
    def create(self,analysis_id:str):

        self._result_parse[analysis_id] = ResultParse(analysis_id,self.event_bus)
    
    async def parse(self,analysis_id):
        await self._result_parse[analysis_id].parse()

    def remove(self,analysis_id:str):
        del self._result_parse[analysis_id]