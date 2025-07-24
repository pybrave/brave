import textwrap
from typing import Any, Optional
from .base_analysis import BaseAnalysis
from brave.api.core.evenet_bus import EventBus
from brave.api.service import pipeline as pipeline_service

class ScriptAnalysis(BaseAnalysis):
    def __init__(self, event_bus:EventBus) -> None:
        super().__init__(event_bus)


    def _get_query_db_field(self, conn, component):
        return ["metaphlan_sam_abundance"]
    
    def _get_command(self,analysis_id,cache_dir,params_path,work_dir,executor_log,component_script,trace_file,workflow_log_file) -> str:
        command =  textwrap.dedent(f"""
            python {component_script} {params_path}
            """)
        return command
    
    def write_config(self,output_dir,component_script):
        script_config_file = f"{output_dir}/main.config"
        return script_config_file
