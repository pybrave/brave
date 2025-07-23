from abc import ABC, abstractmethod
from ast import Dict
import json
import os
from typing import Any, Optional
from brave.api.config.db import get_engine
from fastapi import HTTPException
from brave.api.core.evenet_bus import EventBus
from brave.api.schemas.analysis import AnalysisExecuterModal
import  brave.api.service.pipeline as pipeline_service
import  brave.api.service.analysis_result_service as analysis_result_service
import  brave.api.service.bio_database_service as bio_database_service
from  brave.api.models.core import analysis as t_analysis
from brave.api.config.config import get_settings
from sqlalchemy import select
import textwrap
import uuid
from brave.api.service.pipeline  import find_module
import importlib
from brave.api.utils.get_db_utils import get_ids
from brave.api.core.routers_name import RoutersName
from brave.api.core.event import AnalysisExecutorEvent


class BaseAnalysis(ABC):
    def __init__(self, event_bus:EventBus) -> None:
        self.event_bus = event_bus

    @abstractmethod
    def _get_query_db_field(self,conn,component):
        pass
    
    async def save_analysis(self,conn,request_param,parse_analysis_result,component,is_submit):
        # parse_analysis_result,component = self.get_parames(request_param)


        new_analysis = {
            "project":request_param['project'],
            "analysis_name":request_param['analysis_name'],
            "request_param":json.dumps(request_param),
            # "analysis_method":component_script,
            "component_id":component.component_id,
            "analysis_status": "running" if is_submit else "created"
            # "parse_analysis_module":parse_analysis_module
        }
        # module_dir = pipeline_id
        # if "moduleDir" in component_content:
        #     module_dir = component_content['moduleDir']

        output_dir=None
        work_dir=None
        result = None
        if "analysis_id" in request_param:
            stmt = select(t_analysis).where(t_analysis.c.analysis_id == request_param['analysis_id'])
            result = conn.execute(stmt).mappings().first()
        if result:
            output_dir = result.output_dir
            work_dir = result.work_dir
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            if not os.path.exists(work_dir):
                os.makedirs(work_dir)
            params_path = result.params_path
            command_path = result.command_path

            with open(params_path, "w") as f:
                json.dump(parse_analysis_result,f)
                
            # new_analysis['output_format'] = parse_analysis_result_module
            stmt = t_analysis.update().values(new_analysis).where(t_analysis.c.analysis_id==request_param['analysis_id'])
            conn.execute(stmt)
            find_analysis = dict(result)
            new_analysis ={
                **find_analysis,
                **new_analysis
            }
        else:
            settings = get_settings()
            base_dir = settings.BASE_DIR
            work_dir = settings.WORK_DIR
            str_uuid = str(uuid.uuid4())
    
            # /ssd1/wy/workspace2/nextflow_workspace
            # wrap_analysis_pipline = ""
            # if 'wrap_analysis_pipeline' in request_param:
            # wrap_analysis_pipline = request_param['wrap_analysis_pipeline']

            project_dir = f"{base_dir}/{request_param['project']}"
            trace_file = f"{base_dir}/monitor/{str_uuid}.trace.log"
            workflow_log_file = f"{base_dir}/monitor/{str_uuid}.workflow.log"
            cache_dir = f"{project_dir}/.nextflow"
            if "pipeline_id" in request_param:  
                pipeline_id = request_param['pipeline_id']
                output_dir = f"{project_dir}/{pipeline_id}/{component.component_id}/{str_uuid}"
            else:
                output_dir = f"{project_dir}/{component.component_id}/{str_uuid}"
            # /data/wangyang/nf_work/
            work_dir = f"{work_dir}/{request_param['project']}"
            params_path = f"{output_dir}/params.json"
            command_path= f"{output_dir}/run.sh"

            executor_log = f"{output_dir}/.nextflow.log"
            script_config_file = f"{output_dir}/nextflow.config"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            if not os.path.exists(work_dir):
                os.makedirs(work_dir)
            # 写入脚本
        
            # script_dir = pipeline_id
            # if "scriptDir" in component_content:
            #     script_dir = component_content['scriptDir']
            component_script = find_module(component.namespace,"nextflow",component.component_id,None,"nf")['path']

            # pipeline_script =  f"{get_pipeline_file(pipeline_script)}"
            new_analysis['pipeline_script'] = component_script

            command =  textwrap.dedent(f"""
            export BRAVE_WORKFLOW_ID={str_uuid}
            export NXF_CACHE_DIR={cache_dir}
            nextflow -log {executor_log} run -offline -resume  \\
                -ansi-log false \\
                {component_script} \\
                -params-file {params_path} \\
                -w {work_dir} \\
                -plugins nf-hello@0.7.0 \\
                -with-trace {trace_file} | tee {workflow_log_file}
            """)
    
            
            
            script_config =  textwrap.dedent(f"""
            trace.overwrite = true
          
            """)
            with open(script_config_file, "w") as f:
                f.write(script_config)

            new_analysis['work_dir'] = work_dir
            new_analysis['output_dir'] = output_dir
            new_analysis['params_path'] = params_path
            new_analysis['command_path'] = command_path
            new_analysis['analysis_id'] = str_uuid
            new_analysis['trace_file'] = trace_file
            new_analysis['workflow_log_file'] = workflow_log_file
            new_analysis['executor_log_file'] = executor_log
            new_analysis['script_config_file'] = script_config_file
            
            with open(command_path, "w") as f:
                f.write(command)
            with open(params_path, "w") as f:
                json.dump(parse_analysis_result,f)
            stmt = t_analysis.insert().values(new_analysis)
            conn.execute(stmt)
        if is_submit:
            await self.submit_analysis(new_analysis)
        return new_analysis

    def get_parames(self, conn, request_param: dict[str, Any]):
         # request_param = analysis_input.model_dump_json()
        component_id = request_param['component_id']
        # pipeline_id = request_param['pipeline_id']
        if component_id is None:
            raise HTTPException(status_code=500, detail=f"component_id is None")

        component = pipeline_service.find_pipeline_by_id(conn, component_id)
        if component is None or not hasattr(component, "content"):
            raise HTTPException(status_code=404, detail=f"Component with id {component_id} not found or missing content.")
        component_content = json.loads(component.content)
        query_name_list = self._get_query_db_field(conn,component)

        parse_analysis_result = self.parse_analysis(conn,request_param,component.namespace,component_id,component_content,query_name_list)
        return parse_analysis_result,component
    
        
    
            

            # print()
            # return conn.execute(samples.select()).fetchall()
            # print()
        # return {"msg":"success"}

    def get_database_dict(self,conn,value):
        bio_database = bio_database_service.get_bio_database_by_id(conn,value)
        db_index = bio_database.get("db_index")
        if db_index and db_index!="":
            return {
                "db_index":db_index,
                "path":bio_database.get("path")
            }
        else:
            return {
                "path":bio_database.get("path")
            }

    def parse_analysis(self,conn,request_param,namespace,component_id,component_content,query_name_list):
        module_name = component_content.get('parseAnalysisModule')

        py_module = find_module(namespace,"py_parse_analysis",component_id,module_name,'py')['module']

        # module_name = f'brave.api.parse_analysis.{module_name}'
        # if importlib.util.find_spec(module) is None:
        #     print(f"{module_name}不存在!")
        # else:
        module = importlib.import_module(py_module)

        

        ## 查找输入字段
        
        # if hasattr(module,"get_db_field"):
        #     get_db_field = getattr(module, "get_db_field")
        #     db_field = get_db_field()
        db_ids_dict = {key: get_ids(request_param[key]) for key in query_name_list if key in request_param}
        db_dict = { key:analysis_result_service.find_analyais_result_by_ids(conn,value) for key,value in  db_ids_dict.items()}
        extra_dict={}
        if "upstreamFormJson" in component_content:
            upstream_form_json = component_content['upstreamFormJson']
            upstream_form_json_names = [item['name'] for item in upstream_form_json]
            extra_dict = {key: request_param[key] for key in upstream_form_json_names if key in request_param}


        if "formJson" in component_content:
            form_json = component_content['formJson']
            form_json_names = [item['name'] for item in form_json]
            extra_dict = {key: request_param[key] for key in form_json_names if key in request_param}

        
        database_dict={}
        if "databases" in component_content:
            bio_database = component_content['databases']
            bio_database_data_type_list = [item['name'] for item in bio_database]
            db_ids_dict = {key: request_param[key] for key in bio_database_data_type_list if key in request_param}
            database_dict = { key:self.get_database_dict(conn,value) for key,value in  db_ids_dict.items()}

        args = {
           
            "database_dict":database_dict,
            "extra_dict":extra_dict,
            "analysis_dict":db_dict
        }

        parse_data = getattr(module, "parse_data")

        result = parse_data(**args)
        return result


    def change_status(self,conn,analysis):
        stmt = t_analysis.update().values({"analysis_status":"running"}).where(t_analysis.c.analysis_id==analysis.analysis_id)
        conn.execute(stmt)

    async def submit_analysis(self,analysis):
        analysis = AnalysisExecuterModal(**analysis)
        await self.event_bus.dispatch(RoutersName.ANALYSIS_EXECUTER_ROUTER,AnalysisExecutorEvent.ON_ANALYSIS_SUBMITTED,analysis)
        

