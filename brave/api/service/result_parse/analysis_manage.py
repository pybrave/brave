
from collections import defaultdict

from pydantic import BaseModel
from brave.api.config.db import get_engine
from brave.api.core.evenet_bus import EventBus
import asyncio


from .result_parse import ResultParse
from concurrent.futures import ThreadPoolExecutor, as_completed


class AnalysisManage:
    def __init__(
        self,
        event_bus:EventBus) -> None:
        self._result_parse: dict[str, ResultParse] = defaultdict()
        self.event_bus = event_bus
        self.pool = ThreadPoolExecutor(max_workers=3)
    
    def create(self,analysis_id:str):

        self._result_parse[analysis_id] = ResultParse(analysis_id,self.event_bus)
    
    async def parse(self,analysis_id):
        # pool.submit(self._result_parse[analysis_id].parse(), f"任务-{i}")
        # await self._result_parse[analysis_id].parse()
        loop = asyncio.get_running_loop()
        _result_parse = ResultParse(analysis_id,self.event_bus)
        loop.run_in_executor(
            self.pool,
            lambda: asyncio.run(_result_parse.parse())
        )

    def remove(self,analysis_id:str):
        del self._result_parse[analysis_id]