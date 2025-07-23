import json
from typing import Any, Optional
from .base_analysis import BaseAnalysis
import  brave.api.service.pipeline as pipeline_service
from brave.api.core.evenet_bus import EventBus

class NextflowAnalysis(BaseAnalysis):
    def __init__(self, event_bus:EventBus) -> None:
        super().__init__(event_bus)


    def _get_query_db_field(self,conn,component):
        if component.component_type=="software":
            component_file_list = pipeline_service.find_component_by_parent_id(conn,component.component_id,"software_input_file")
            component_file_name_list = [json.loads(item.content)['name'] for item in component_file_list]
            return component_file_name_list
        elif component.component_type == "script":
            return ['metaphlan_sam_abundance']
    