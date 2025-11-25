from abc import ABC, abstractmethod
from ast import Dict
import json
import os
from typing import Any, Optional
from brave.api.config.db import get_engine
from fastapi import HTTPException
from brave.api.core.evenet_bus import EventBus
from brave.api.enum.component_script import ScriptName
from brave.api.schemas.analysis import AnalysisExecuterModal
import  brave.api.service.pipeline as pipeline_service
import  brave.api.service.analysis_result_service as analysis_result_service
import  brave.api.service.bio_database_service as bio_database_service
from  brave.api.models.core import analysis as t_analysis
from brave.api.config.config import get_settings
from sqlalchemy import select
import textwrap
import uuid
import importlib
from brave.api.utils.get_db_utils import get_colors, get_ids,get_group, get_re_group

from brave.api.core.routers_name import RoutersName
from brave.api.core.event import AnalysisExecutorEvent
from brave.api.service import namespace_service, project_service, sample_service


class BaseAnalysis(ABC):
    def __init__(self, event_bus:EventBus) -> None:
        self.event_bus = event_bus

    # @abstractmethod
    # def _get_query_db_field(self,conn,component):
    #     pass
    #   "3c80793f-ff1b-44d1-82bd-5b1ed82469f2":{
    #     "type":"BaseSelect"
    #   },
    def get_file_form(self,file_item,component):

        content = json.loads(file_item.content)
        if file_item.component_id in component:
            form_filed = component[file_item.component_id]
            content = {
                **content,
                **form_filed
            }
        return content
    def _get_query_db_field(self,conn,component):
        if component['component_type']=="software":
            component_file_name_list = {}
            if "reInputFile" in component:
                re_input_file = component['reInputFile']
                component_file_name_list = {item['name']:item for item in re_input_file}
            else:
                component_file_list = pipeline_service.find_component_by_parent_id(conn,component['component_id'],"software_input_file")
                component_file_name_list = {json.loads(item.content)['name']:self.get_file_form(item,component) for item in component_file_list}
                
            return component_file_name_list
        elif component['component_type'] == "script":
            if "formJson" in component:
                return {item['name']:item for item in component['formJson'] if "db" in item and  item['db']}
        elif component['component_type'] == "pipeline":
            input_file_list = component['inputFile']
            return {item['name']:item for item in input_file_list}
        return []

    @abstractmethod
    def _get_command(self,analysis_id,output_dir,cache_dir,params_path,work_dir,executor_log,component_script,trace_file,workflow_log_file,pieline_dir_with_namespace,script_type) -> str:
        pass
    
    @abstractmethod
    def write_config(self,output_dir,analysis_id,component,more_params) -> str:
        pass
    
  



    async def save_analysis(self,conn,request_param,parse_analysis_result,component,is_report):
        # parse_analysis_result,component = self.get_parames(request_param)


        new_analysis = {
            "project":request_param['project'],
            "analysis_name":request_param['analysis_name'],
            "request_param":json.dumps(request_param),
            # "analysis_method":component_script,
            "component_id":component['component_id'],
            "is_report":is_report,
            # "is_report":request_param['is_report'] if "is_report" in request_param else False,
            "data_component_ids":request_param['data_component_ids'],
            # "parse_analysis_module":parse_analysis_module
        }
        new_analysis = {k:v for k,v in new_analysis.items() if v is not None}
        # module_dir = pipeline_id
        # if "moduleDir" in component_content:
        #     module_dir = component_content['moduleDir']
        more_params = {}
        used_namespace = namespace_service.get_used_namespace(conn)
        if used_namespace:
            if used_namespace.volumes:
                volumes_dict = json.loads(used_namespace.volumes)
                more_params["volumes"] = " ".join([
                    f"-v {host}:{conf['bind']}:{conf.get('mode', 'rw')}"
                    for host, conf in volumes_dict.items()
                ])
            if used_namespace.resources:
                more_params["process"] = "\n\t".join([
                    f"{key}=\"{value}\""
                    for key, value in json.loads(used_namespace.resources).items()
                ])
            if used_namespace.queue_size:
                more_params["queue_size"] = used_namespace.queue_size
     
        

        output_dir=None
        work_dir=None
        result = None
        if "analysis_id" in request_param:
            stmt = select(t_analysis).where(t_analysis.c.analysis_id == request_param['analysis_id'])
            result = conn.execute(stmt).mappings().first()
        if result:
            print("update analysis")
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

            # new_analysis['container_id'] = component["container_id"]
            if  result.job_status != "running":
                new_analysis["job_status"] = "updated"
            # new_analysis['output_format'] = parse_analysis_result_module
            self.write_config(output_dir,result.analysis_id,component,more_params)

            stmt = t_analysis.update().values(new_analysis).where(t_analysis.c.analysis_id==request_param['analysis_id'])
            conn.execute(stmt)
            find_analysis = dict(result)
            new_analysis ={
                **find_analysis,
                **new_analysis
            }
        else:
            print("create analysis")
            settings = get_settings()
            base_dir = settings.BASE_DIR
            analsyis_dir = settings.ANALYSIS_DIR
            work_dir = settings.WORK_DIR
            pieline_dir = settings.PIPELINE_DIR
            str_uuid = str(uuid.uuid4())
            pieline_dir_with_namespace = f"{pieline_dir}"
            # /ssd1/wy/workspace2/nextflow_workspace
            # wrap_analysis_pipline = ""
            # if 'wrap_analysis_pipeline' in request_param:
            # wrap_analysis_pipline = request_param['wrap_analysis_pipeline']
            

            project_dir = f"{analsyis_dir}/{request_param['project']}"
            trace_file = f"{base_dir}/monitor/{str_uuid}.trace.log"
            workflow_log_file = f"{base_dir}/monitor/{str_uuid}.workflow.log"
            # if "pipeline_id" in request_param:  
            #     pipeline_id = request_param['pipeline_id']
            #     output_dir = f"{project_dir}/{pipeline_id}/{component['component_id']}/{str_uuid}"
            # else:
            output_dir = f"{project_dir}/{component['component_id']}/{str_uuid}"
            # /data/wangyang/nf_work/
            work_dir = f"{work_dir}/{request_param['project']}/{component['component_id']}/{str_uuid}"
            params_path = f"{output_dir}/params.json"
            command_path= f"{output_dir}/run.sh"
            command_log_path= f"{output_dir}/run.log"
            # cache_dir = f"{project_dir}/.nextflow"
            cache_dir = f"{output_dir}/.nextflow"
            executor_log = f"{output_dir}/.nextflow.log"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            if not os.path.exists(work_dir):
                os.makedirs(work_dir)
            # 写入脚本
        
            # script_dir = pipeline_id
            # if "scriptDir" in component_content:
            #     script_dir = component_content['scriptDir']
            component_script = pipeline_service.find_component_module(component,ScriptName.main)['path']

            new_analysis['pipeline_script'] = component_script
            command = self._get_command(str_uuid,output_dir,cache_dir,params_path,work_dir,executor_log,component_script,trace_file,workflow_log_file,pieline_dir_with_namespace,component["script_type"])

            # command =  textwrap.dedent(f"""
            # export BRAVE_WORKFLOW_ID={str_uuid}
            # export NXF_CACHE_DIR={cache_dir}
            # nextflow -log {executor_log} run -offline -resume  \\
            #     -ansi-log false \\
            #     {component_script} \\
            #     -params-file {params_path} \\
            #     -w {work_dir} \\
            #     -plugins nf-hello@0.7.0 \\
            #     -with-trace {trace_file} | tee {workflow_log_file}
            # """)
    
            
            # script_config_file = f"{output_dir}/nextflow.config"
            # script_config =  textwrap.dedent(f"""
            # trace.overwrite = true
          
            # """)
            # with open(script_config_file, "w") as f:
            #     f.write(script_config)

            new_analysis['work_dir'] = work_dir
            new_analysis['output_dir'] = output_dir
            new_analysis['params_path'] = params_path
            new_analysis['command_path'] = command_path
            new_analysis['analysis_id'] = str_uuid
            request_param["analysis_id"] = str_uuid
            new_analysis["request_param"] = json.dumps(request_param)
            new_analysis['trace_file'] = trace_file
            new_analysis['workflow_log_file'] = workflow_log_file
            new_analysis['executor_log_file'] = executor_log

            script_config_file = self.write_config(output_dir,str_uuid,component,more_params)

            new_analysis['script_config_file'] = script_config_file
            new_analysis['command_log_path'] = command_log_path
            # new_analysis['container_id'] = component["container_id"]
            new_analysis["job_status"] = "created"
            with open(command_path, "w") as f:
                f.write(command)
            with open(params_path, "w") as f:
                json.dump(parse_analysis_result,f)
            stmt = t_analysis.insert().values(new_analysis)
            conn.execute(stmt)
        # if is_submit:
            # await self.submit_analysis(new_analysis)
        return new_analysis

    

    def get_parames(self, conn, request_param: dict[str, Any],component):
         # request_param = analysis_input.model_dump_json()
        # component_id = request_param['component_id']
        # pipeline_id = request_param['pipeline_id']
        # if component_id is None:
        #     raise HTTPException(status_code=500, detail=f"component_id is None")

        # component = pipeline_service.find_pipeline_by_id(conn, component_id)
        # if component is None or not hasattr(component, "content"):
        #     raise HTTPException(status_code=404, detail=f"Component with id {component.component_id} not found or missing content.")
        query_name_dict = self._get_query_db_field(conn,component)
        # query_name_list_keys = list(query_name_list.keys())
        parse_analysis_result = self.parse_analysis(conn,request_param,component,query_name_dict)
        return parse_analysis_result
    
        
    
            

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

    def parse_analysis(self,conn,request_param,component,query_name_dict):
        query_name_list = list(query_name_dict.keys())

        module_info = pipeline_service.find_component_module(component, ScriptName.input_parse)
        if not module_info:
            raise HTTPException(status_code=500, detail=f"组件{component['component_id']}的输入解析模块没有找到!")
        py_module = module_info['module']
    
        module = importlib.import_module(py_module)

        

    
        db_ids_dict = {key: get_ids(request_param[key]) for key in query_name_list if key in request_param}
        db_dict = { key:analysis_result_service.find_analyais_result_by_ids(conn,value) for key,value in  db_ids_dict.items()}
        project_list = [item["project"] for item_list in db_dict.values() for item in item_list]
        project_list = list(set(project_list))
        metadata_form =[]
        if len(project_list)>0:
            project_list =  project_service.find_by_project_ids(conn,project_list)
            metadata_form = [json.loads(item["metadata_form"]) for item in project_list if item["metadata_form"]]
            metadata_form = [item for item_list in metadata_form for item in item_list if item is not None]

        
        samples_dict = {}
        if "project" in request_param:
            samples_list = sample_service.find_by_project(conn,request_param["project"])
            samples_dict = { sample["sample_name"]:sample for sample in samples_list}
        
        groups_name = {key:get_group(request_param[key]) for key in query_name_list if key in request_param }
        re_groups_name = {key:get_re_group(request_param[key]) for key in query_name_list if key in request_param }
        colors = {key:get_colors(request_param[key]) for key in query_name_list if key in request_param }
        
        for k,v in db_dict.items():
           
            query_form = query_name_dict.get(k,{})
            query_form_type = query_form["type"]
            if query_form_type =="CollectedGroupSelectSampleButton" and "columns"in query_form:
                analysis_result = v[0]
                columns = query_form["columns"]
                analysis_result["form_type"] = query_form_type
                analysis_result["groups"] = columns
                for column_group in columns:
                    columns = request_param[k][column_group]
                    columns = [ analysis_result_service.build_collected_analysis_result(item,analysis_result,samples_dict)
                        for item in columns
                    ]
                    columns = [ {**item,
                        "selcted_group_name":groups_name[k].get(column_group),
                        "re_groups_name":re_groups_name[k].get(column_group)}for item in columns ]
                    analysis_result[column_group] = columns

                db_dict[k] = analysis_result
            else:
                ids = db_ids_dict[k]
                # for single select
                if isinstance(ids,list):
                    db_dict[k] = [ {**item,
                        "form_type":query_form_type,
                        "selcted_group_name":groups_name.get(k),
                        "re_groups_name":re_groups_name.get(k)}for item in v ]
                else:
                    db_dict[k] = {**v[0],
                        "form_type":query_form_type,
                        "selcted_group_name":groups_name.get(k),
                        "re_groups_name":re_groups_name.get(k)}


        # def get_columns(values,samples_dict,analsyis_result):
        #     if isinstance(values, dict):
        #         if "file" in  values:
        #             analsyis_result_dict = {item["id"]:item for item in analsyis_result}
        #             analsyis_result_dict_one = analsyis_result_dict.get(values["file"],{})
        #             # 根据column获取metadata
        #             columns = [ analysis_result_service.build_collected_analysis_result(item,analsyis_result_dict_one,samples_dict)
        #                 for item in values["columns"]
        #             ]
        #             return columns
        #         elif "columns" in values:
        #             columns = [ analysis_result_service.build_collected_analysis_result(item,{},samples_dict)
        #                 for item in values["columns"]
        #             ]
        #             return columns
                
        #     return "-"

        # file_columns = {key:get_columns(request_param[key],samples_dict,db_dict[key]) for key in query_name_list if key in request_param }

      

        extra_dict={}
        if "upstreamFormJson" in component:
            upstream_form_json = component['upstreamFormJson']
            upstream_form_json_names = [item['name'] for item in upstream_form_json]
            extra_dict = {key: request_param[key] for key in upstream_form_json_names if key in request_param}
            inner_params =  {k:v for k,v in  request_param.items() if k.startswith("__")}
            extra_dict.update(inner_params)


        if "formJson" in component:
            form_json = component['formJson']
            form_json_names = [item['name'] for item in form_json if item["type"]!="Divider"]
            extra_dict = {key: request_param[key] for key in form_json_names if key in request_param}
            inner_params =  {k:v for k,v in  request_param.items() if k.startswith("__")}
            extra_dict.update(inner_params)

        
        database_dict={}
        if "databases" in component:
            bio_database = component['databases']
            bio_database_data_type_list = [item['name'] for item in bio_database]
            db_ids_dict = {key: request_param[key] for key in bio_database_data_type_list if key in request_param}
            database_dict = { key:self.get_database_dict(conn,value) for key,value in  db_ids_dict.items()}

        settings = get_settings()
        args = {
           "re_groups_name":re_groups_name,
           "colors":colors,
            "database_dict":database_dict,
            "extra_dict":extra_dict,
            "analysis_dict":db_dict,
            "groups_name":groups_name,
            "groups":query_name_list,
            # "file_columns":file_columns,
            "settings":settings,
            "metadata_form":metadata_form
        }

        parse_data = getattr(module, "parse_data")

        result = parse_data(**args)
        return result


    def change_status(self,conn,analysis):
        stmt = t_analysis.update().values({"job_status":"running"}).where(t_analysis.c.analysis_id==analysis.analysis_id)
        conn.execute(stmt)


    # async def submit_analysis(self,analysis):
    #     analysis = AnalysisExecuterModal(**analysis)
    #     await self.event_bus.dispatch(RoutersName.ANALYSIS_EXECUTER_ROUTER,AnalysisExecutorEvent.ON_ANALYSIS_SUBMITTED,analysis)
        

