from typing import Any, Optional
from .base_analysis import BaseAnalysis
from brave.api.core.evenet_bus import EventBus

class ScriptAnalysis(BaseAnalysis):
    def __init__(self, event_bus:EventBus) -> None:
        super().__init__(event_bus)


    def _get_query_db_field(self, conn, component):
        return ["metaphlan_sam_abundance"]
    