import textwrap
import os
from typing import Any, Optional
from .base_analysis import BaseAnalysis
from brave.api.core.evenet_bus import EventBus
from brave.api.service import pipeline as pipeline_service

class ScriptAnalysis(BaseAnalysis):
    def __init__(self, event_bus:EventBus) -> None:
        super().__init__(event_bus)


    # def _get_query_db_field(self, conn, component):
    #     return ["metaphlan_sam_abundance"]
    
    def _get_command(self,analysis_id,output_dir,cache_dir,params_path,work_dir,executor_log,component_script,trace_file,workflow_log_file,pieline_dir_with_namespace,script_type) -> str:
        output_path = f"{output_dir}/output"
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        language = ""
        if  script_type == "python":
            language = "python -u"
        elif script_type == "r":
            language = "Rscript"
        elif script_type == "shell":
            language = "bash"
        elif script_type == "jupyter":
            language = "ipython"
        command =  textwrap.dedent(f"""
            {language} {component_script} {params_path}  {output_path}
            """)
        return command
    
    def write_config(self,output_dir,analysis_id,component,more_params):
        script_config_file = f"{output_dir}/main.config"
        return script_config_file
