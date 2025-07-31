from anyio import Event
from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from fastapi import APIRouter,Depends,HTTPException, Request
from sqlalchemy.orm import Session
# from brave.api.config.db import conn
from brave.api.core.evenet_bus import EventBus
from brave.api.executor.models import LocalJobSpec
from brave.api.schemas.bio_database import QueryBiodatabase
from brave.api.schemas.sample import Sample
from typing import List
from starlette.status import HTTP_204_NO_CONTENT
from sqlalchemy import func, select
from brave.api.models.orm import SampleAnalysisResult
import glob
import importlib
import os
from brave.api.config.db import get_db_session
from sqlalchemy import and_,or_
import pandas as pd
from brave.api.models.core import samples
from brave.api.config.db import get_engine
from brave.api.schemas.analysis import AnalysisInput,Analysis,QueryAnalysis,AnalysisExecuterModal
from typing import Dict, Any
from brave.api.models.core import analysis
import json
import importlib
import importlib.util
import uuid
import os
from brave.api.service.result_parse import script_analysis
from brave.api.service.result_parse import nextflow_analysis
from brave.api.service.result_parse.nextflow_analysis    import NextflowAnalysis
from brave.api.utils.get_db_utils import get_ids
from brave.api.config.config import get_settings
from brave.api.routes.pipeline import get_pipeline_file
import textwrap
# from brave.api.routes.sample_result import find_analyais_result_by_ids
from brave.api.routes.sample_result import parse_result_one
import  brave.api.service.pipeline as pipeline_service
import brave.api.service.bio_database_service as bio_database_service
import inspect
from typing import Optional
import pandas as pd
import subprocess
from brave.api.service.watch_service import queue_process
import threading
import psutil
import brave.api.service.analysis_result_service as analysis_result_service
import brave.api.service.sample_service as sample_service
import brave.api.service.analysis_service as analysis_service
from brave.api.service.analysis_result_parse import AnalysisResultParse
from brave.app_container import AppContainer
from brave.app_manager import AppManager
from brave.api.executor.base import JobExecutor
from brave.api.core.routers_name import RoutersName
from brave.api.core.event import AnalysisExecutorEvent
from brave.api.service.result_parse.script_analysis import ScriptAnalysis
from brave.api.service.result_parse.nextflow_analysis import NextflowAnalysis
analysis_api = APIRouter()


def update_or_save_result(db,project,sample_name,file_type,file_path,log_path,verison,analysis_name,software):
        sampleAnalysisResult = db.query(SampleAnalysisResult) \
        .filter(and_(SampleAnalysisResult.analysis_name == analysis_name,\
                SampleAnalysisResult.analysis_verison == verison, \
                SampleAnalysisResult.sample_name == sample_name, \
                SampleAnalysisResult.file_type == file_type, \
                SampleAnalysisResult.project == project \
            )).first()
        if sampleAnalysisResult:
            sampleAnalysisResult.contant_path = file_path
            sampleAnalysisResult.log_path = log_path
            sampleAnalysisResult.software = software
            db.commit()
            db.refresh(sampleAnalysisResult)
            print(">>>>更新: ",file_path,sample_name,file_type,log_path)
        else:
            sampleAnalysisResult = SampleAnalysisResult(analysis_name=analysis_name, \
                analysis_verison=verison, \
                sample_name=sample_name, \
                file_type=file_type, \
                log_path=log_path, \
                software=software, \
                project=project, \
                contant_path=file_path \
                    )
            db.add(sampleAnalysisResult)
            db.commit()
            print(">>>>新增: ",file_path,sample_name,file_type,log_path)


# def get_db_value(session, value):
#     ids = value
#     if not isinstance(value,list):
#         ids = [value]
#     analysis_result =  session.query(SampleAnalysisResult) \
#                 .filter(SampleAnalysisResult.id.in_(ids)) \
#                     .all()
                    
#     for item in analysis_result:
#         if item.content_type=="json" and not isinstance(item.content, dict):
#             item.content = json.loads(item.content)

#     if len(analysis_result)!=len(ids):
#         raise HTTPException(status_code=500, detail="数据存在问题!")
#     if not isinstance(value,list) and len(analysis_result)==1:
#         return analysis_result[0]
#     else:
#         return analysis_result
    




 

        # get_script = getattr(module, "get_script")
        # script = get_script()
        # command = f"nextflow run -offline {script} -resume  -params-file {params_path} -w {work_dir} -with-trace trace.txt | tee .workflow.log"
        # with open(command_path, "w") as f:
        #     f.write(command)
        # get_output_format = getattr(module, "get_output_format")
        # output_format = get_output_format()
        # return json.dumps(output_format)

# ,response_model=List[Sample]
#  参数解析


def get_all_files_recursive_v2(directory):
    file_list=[]
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file).replace(directory,""))
    return file_list




@analysis_api.get("/analysis/browse-output-dir/{analysis_id}")
async def browse_output_dir(analysis_id):
   with get_engine().begin() as conn:
        stmt = select(analysis).where(analysis.c.analysis_id == analysis_id)
        result = conn.execute(stmt).mappings().first()
        if not result:
            raise HTTPException(status_code=404, detail=f"Analysis with id {analysis_id} not found")
        output_dir = result['output_dir']
        file_list = get_all_files_recursive_v2(output_dir)
        return file_list

# 结果解析

@analysis_api.post("/fast-api/parse-analysis-result/{analysis_id}")
@inject
async def parse_analysis_result(
    analysis_id,save:Optional[bool]=False,
    analysis_result_parse_service:AnalysisResultParse = Depends(Provide[AppContainer.analysis_result_parse_service])):
    with get_engine().begin() as conn:
        if save:
            result = await analysis_result_parse_service.save_analysis_result_preview(conn,analysis_id)
        else:
            result = await analysis_result_parse_service.parse_analysis_result_preview(conn,analysis_id)
        return result
    #     params :Any = analysis_service.get_parse_analysis_result_params(conn,analysis_id)
    #     result_list,result_dict = analysis_service.execute_parse(**params)


    #     analysis :Any = params["analysis"]
    #     file_format_list = params["file_format_list"]
    #     file_dict = analysis_service.get_file_dict(file_format_list,analysis['output_dir'])
            
    #     if save:
    #         for item in result_list:
    #             result = analysis_result_service.find_analysis_result_exist(conn,item['component_id'],item['file_name'],item['project'])
    #             if not result:
    #                 find_sample = sample_service.find_by_sample_name_and_project(conn,item['sample_name'],item['project'])
    #                 if find_sample:
    #                     item['sample_id'] = find_sample['sample_id']
    #                 analysis_result_service.add_analysis_result(conn,item)
    #             else:
    #                 if item['analysis_result_hash']!= result['analysis_result_hash']:
    #                     analysis_result_service.update_analysis_result(conn,result.id,item)
                    
    #         # sample_name_list = [item['file_name'] for item in result_list]
    #         # sample_list = sample_service.find_by_sample_name_list(conn,sample_name_list)
    #         # sample_dict = {item['sample_name']:item for item in sample_list}
    #         # for item in result_list:
    #         #     if item['file_name'] in sample_dict:
    #         #         item['sample_id'] = sample_dict[item['file_name']]['sample_id']
    #         #     else:
    #         #         raise HTTPException(status_code=500, detail=f"样本{item['file_name']}不存在!")
    #         # analysis_result_service.save_or_update_analysis_result_list( conn,result_list)
    #         # parse_result_oneV2(res,item['name'],result['project'],"V1.0",analysis_id)
    # return {"result_dict":result_dict,"file_format_list":file_format_list,"file_dict":file_dict}



@analysis_api.post(
    "/list-analysis",
    # response_model=List[Analysis],
)
async def list_analysis(query:QueryAnalysis):
    with get_engine().begin() as conn:
        return  analysis_service.list_analysis(conn,query)


@analysis_api.delete("/fast-api/analysis/{id}",  status_code=HTTP_204_NO_CONTENT)
def delete_analysis(id: int):
    with get_engine().begin() as conn:
        conn.execute(analysis.delete().where(analysis.c.id == id))
    return {"message":"success"}




def pileine_analysis_run_log(result,type):
    if type == "workflow_log":
        workflow_log_file = result.workflow_log_file
        if workflow_log_file and os.path.exists(workflow_log_file):
            with open(workflow_log_file, "r") as f:
                params =f.read()
            return params
    elif type == "executor_log":
        executor_log_file = result.executor_log_file
        if executor_log_file and os.path.exists(executor_log_file):
            with open(executor_log_file, "r") as f:
                params =f.read()
            return params
    elif type == "params":
        params_path = result.params_path
        if params_path and os.path.exists(params_path):
            with open(params_path, "r") as f:
                params = json.load(f)
            return params
    elif type == "script_config":
        script_config_file = result.script_config_file
        if script_config_file and os.path.exists(script_config_file):
            with open(script_config_file, "r") as f:
                params = f.read()
            return params
    elif type == "trace":
        trace_file = result.trace_file
        trace =[]
        total = 0
        if trace_file and os.path.exists(trace_file):
            df = pd.read_csv(trace_file,sep="\t")
            total = df.shape[0]
            trace = df.to_dict(orient="records")
        
        return {
            "traceTable":trace,
            "total":total,
            "process_id":result.process_id,
            "status":"running" if result.process_id else "finished"
        }
    return ""


@analysis_api.get("/monitor-analysis/{analysis_id}")
async def pipeline_monitor(analysis_id,type):
    with get_engine().begin() as conn:
        stmt = select(analysis).where(analysis.c.analysis_id == analysis_id)
        result = conn.execute(stmt)
        result = result.mappings().first()
    return pileine_analysis_run_log(result,type)
    # analysis_ = rows[len(rows)-1]
    # output_dir = analysis_['output_dir']
    
# import asyncio
# import time
# import threading
# def blocking_task():
#     print(f"开始阻塞任务，线程: {threading.current_thread().name}")
#     time.sleep(5)
#     print("阻塞任务完成")

def start_background( cwd,cmd):
    proc = subprocess.Popen(
        cmd,
        cwd=cwd, 
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    threading.Thread(target=proc.wait, daemon=True).start() # 处理僵尸进程
    return proc.pid

@analysis_api.post("/run-analysis/{analysis_id}")
@inject
async def run_analysis(
    request: Request,
    analysis_id,
    auto_parse:Optional[bool]=True,
    analysis_result_parse_service:AnalysisResultParse = Depends(Provide[AppContainer.analysis_result_parse_service])         
    ):

    manager: AppManager = request.app.state.manager  # 从 app.state 获取实例
    process_monitor = manager.process_monitor
    if process_monitor is None:
        raise HTTPException(status_code=500, detail="ProcessMonitor服务未初始化")
    
    with get_engine().begin() as conn:
        stmt = select(analysis).where(analysis.c.analysis_id == analysis_id)
        result = conn.execute(stmt)
        analysis_ = result.mappings().first()
        process_id = analysis_.process_id
        if process_id is not None:
            try:
                proc = psutil.Process(int(process_id))
                if proc.is_running():
                    raise Exception(f"Analysis is already running with process_id={process_id}")
            except (psutil.NoSuchProcess, ValueError):
                pass  # 进程不存在或 process_id 非法，继续执行
        
        pid = start_background(analysis_.output_dir, ["bash","run.sh"])
        stmt = analysis.update().values({"process_id":pid,"analysis_status":"running"}).where(analysis.c.analysis_id==analysis_id)
        conn.execute(stmt)
        analysis_dict = dict(analysis_)

        analysis_dict['process_id'] = pid
        # await queue_process.put(analysis_dict)
        await process_monitor.add_process(analysis_dict)
        if auto_parse:
            await analysis_result_parse_service.add_analysis_id(analysis_id)
    return {"pid":pid}




# @analysis_api.post("/fast-api/save-analysis")
# @inject
# async def save_analysis(
#     request_param: Dict[str, Any],
#     save:Optional[bool]=False,
#     is_submit:Optional[bool]=False,
#     software_analysis:NextflowAnalysis  =Depends(Provide[AppContainer.nextflow_analysis])): # request_param: Dict[str, Any]
#     with get_engine().begin() as conn:
#         parse_analysis_result,component = software_analysis.get_parames(conn,request_param)
#         if not save:
#             return parse_analysis_result
#         return await software_analysis.save_analysis(conn,request_param,parse_analysis_result,component,is_submit) 
  
    # return software_analysis.save_analysis(request_param)
    # return {"msg":"success"}


@analysis_api.post("/fast-api/analysis-controller")
@inject
async def save_script_analysis(
    request_param: Dict[str, Any],
    # type:Optional[str]="nextflow",
    save:Optional[bool]=False,
    is_submit:Optional[bool]=False,
    app_container:AppContainer = Depends(Provide[AppContainer])
    ): # request_param: Dict[str, Any]
    
    
    if  type=="script":
        analysis_controller = app_container.script_analysis()
    else:
        analysis_controller = app_container.nextflow_analysis()

    with get_engine().begin() as conn:
        component_id = request_param['component_id']
        # pipeline_id = request_param['pipeline_id']
        if component_id is None:
            raise HTTPException(status_code=500, detail=f"component_id is None")
        component = pipeline_service.find_pipeline_by_id(conn, component_id)
        if component.component_type == "pipeline":
            component = pipeline_service.get_pipeline_v2(conn,component_id)
        if component is None:
            raise HTTPException(status_code=404, detail=f"Component with id {component_id} not found")
        if component is None or "content" not in component:
            raise HTTPException(status_code=404, detail=f"Component with id {component.component_id} not found or missing content.")
        
        # component_content = 
        component_obj = {
            **{ k:v for k,v in component.items() if k != "content"},
            **json.loads(component['content'])
        }
        script_type = component_obj['script_type']
        if script_type == "python" or script_type == "shell" or script_type == "r":
            analysis_controller = app_container.script_analysis()
        else:
            analysis_controller = app_container.nextflow_analysis()

        parse_analysis_result = analysis_controller.get_parames(conn,request_param,component_obj)

        if not save:
            return parse_analysis_result
        return await analysis_controller.save_analysis(conn,request_param,parse_analysis_result,component_obj,is_submit) 
  


@analysis_api.get("/get-executor-logs/{analysis_id}")
@inject
def get_executor_logs(analysis_id,job_executor_selector:JobExecutor = Depends(Provide[AppContainer.job_executor_selector])):
    return job_executor_selector.get_logs(analysis_id)




@analysis_api.post("/run-analysis-v2/{analysis_id}")
@inject
async def run_analysis_v2(
    analysis_id,
    auto_parse:Optional[bool]=True,
    # executor: JobExecutor = Depends(get_executor_dep),
    evenet_bus:EventBus = Depends(Provide[AppContainer.event_bus]) 
    ):

    # manager: AppManager = request.app.state.manager  # 从 app.state 获取实例
    # process_monitor = manager.process_monitor
    # if process_monitor is None:
    #     raise HTTPException(status_code=500, detail="ProcessMonitor服务未初始化")
    
    with get_engine().begin() as conn:
        stmt = select(analysis).where(analysis.c.analysis_id == analysis_id)
        result = conn.execute(stmt)
        analysis_ = result.mappings().first()
        if analysis_ is None:
            raise HTTPException(status_code=404, detail="Analysis not found")
        # process_id = analysis_['process_id']
        analysis_ = AnalysisExecuterModal(**analysis_)
        stmt = analysis.update().values({"analysis_status":"running"}).where(analysis.c.analysis_id==analysis_id)
        conn.execute(stmt)
        await evenet_bus.dispatch(RoutersName.ANALYSIS_EXECUTER_ROUTER,AnalysisExecutorEvent.ON_ANALYSIS_SUBMITTED,analysis_)
        
        
        # job_id = await executor.submit_job(LocalJobSpec(
        #     job_id=analysis_id,
        #     command=["bash", "run.sh"],
        #     output_dir=analysis_['output_dir'],
        #     process_id=analysis_['process_id']
        # ))
    
        return {"msg":"success"}

    #     analysis_dict = dict(analysis_)
    #     analysis_dict['job_id'] = job_id
    #     await process_monitor.add_process(analysis_dict)
    #     if auto_parse:
    #         await analysis_result_parse_service.add_analysis_id(analysis_id)
    #     if process_id is not None:
    #         try:
    #             proc = psutil.Process(int(process_id))
    #             if proc.is_running():
    #                 raise Exception(f"Analysis is already running with process_id={process_id}")
    #         except (psutil.NoSuchProcess, ValueError):
    #             pass  # 进程不存在或 process_id 非法，继续执行
        
    #     pid = start_background(analysis_.output_dir, ["bash","run.sh"])
    #     stmt = analysis.update().values({"process_id":pid,"analysis_status":"running"}).where(analysis.c.analysis_id==analysis_id)
    #     conn.execute(stmt)
    #     analysis_dict = dict(analysis_)

    #     analysis_dict['process_id'] = pid
    #     # await queue_process.put(analysis_dict)
    #     await process_monitor.add_process(analysis_dict)
    #     if auto_parse:
    #         await analysis_result_parse_service.add_analysis_id(analysis_id)
    # return {"pid":pid}


# @analysis_api.get("/monitor-analysis/{analysis_id}")
# async def pipeline_monitor(analysis_id):
#     with get_engine().begin() as conn:
#         stmt = select(analysis).where(analysis.c.id == analysis_id)
#         result = conn.execute(stmt)
#         result = result.mappings().fetchone()
#     if not result:
#         return {}

#     output_dir = result['output_dir']
#     trace_file = f"{output_dir}/trace.txt"
#     if os.path.exists(trace_file):
#         df = pd.read_csv(trace_file,sep="\t")
#     return  df.to_dict(orient="records")   

@analysis_api.get("/find-analysis-by-id/{analysis_id}") 
async def find_analysis_by_id(analysis_id):
    settings = get_settings()
    with get_engine().begin() as conn:
        stmt = select(analysis).where(analysis.c.analysis_id == analysis_id)
        result = conn.execute(stmt)
        analysis_ = result.mappings().first()
        if analysis_ is None:
            raise HTTPException(status_code=404, detail="Analysis not found")
        analysis_dict = dict(analysis_)
        script_dir = analysis_dict['pipeline_script']
        script_dir = os.path.dirname(script_dir).replace(str(settings.PIPELINE_DIR)+"/","")
        jupyter_notebook_path =  f"{script_dir}/main.ipynb"
        analysis_dict["jupyter_notebook_path"] = jupyter_notebook_path
        return analysis_dict



@analysis_api.get("/get-cache-analysis-result-by-id/{analysis_id}")
@inject
async def get_cache_analysis_result_by_id(analysis_id,analysis_result_parse_service:AnalysisResultParse = Depends(Provide[AppContainer.analysis_result_parse_service])):
    return analysis_result_parse_service.cached_analysis_result()[analysis_id]

@analysis_api.get("/get-cache-analysis-result")
@inject
async def get_cache_analysis_result(analysis_result_parse_service:AnalysisResultParse = Depends(Provide[AppContainer.analysis_result_parse_service])):
    return analysis_result_parse_service.cached_analysis_result()


@analysis_api.get("/get-cache-analysis-params")
@inject
async def get_cache_params(analysis_result_parse_service:AnalysisResultParse = Depends(Provide[AppContainer.analysis_result_parse_service])):
    return analysis_result_parse_service.cached_params()



