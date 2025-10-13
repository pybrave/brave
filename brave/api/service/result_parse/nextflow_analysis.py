import json
import os
import textwrap
from typing import Any, Optional
from .base_analysis import BaseAnalysis
import  brave.api.service.pipeline as pipeline_service
from brave.api.core.evenet_bus import EventBus

class NextflowAnalysis(BaseAnalysis):
    def __init__(self, event_bus:EventBus) -> None:
        super().__init__(event_bus)



    
    

    def _get_command(self,analysis_id,output_dir,cache_dir,params_path,work_dir,executor_log,component_script,trace_file,workflow_log_file,pieline_dir_with_namespace,script_type) -> str:
        nextflow_config =  f"{pieline_dir_with_namespace}/nextflow.config"
        if  not os.path.exists(nextflow_config):
            # config_arg = f" -c {nextflow_config}"
            with open(nextflow_config,"w") as f:
                f.write("")
        command =  textwrap.dedent(f"""
            export BRAVE_WORKFLOW_ID={analysis_id}
            export NXF_CACHE_DIR={cache_dir}
            nextflow -log {executor_log} run -offline -resume  \\
                -ansi-log false \\
                {component_script} \\
                -params-file {params_path} \\
                -w {work_dir} \\
                -c {nextflow_config} \\
                -with-trace {trace_file} | tee {workflow_log_file} ; exit ${{PIPESTATUS[0]}}
            """)
        # -plugins nf-hello@0.7.0 \\

        return command
        
    def write_config(self,output_dir,component_script):
        script_config_file = f"{output_dir}/nextflow.config"
        script_config =  textwrap.dedent(f"""
        trace.overwrite = true
        docker{{
            enabled = true
            runOptions = '--user $(id -u):$(id -g)'
        }}
        """)
        with open(script_config_file, "w") as f:
            f.write(script_config)
        return script_config_file
  