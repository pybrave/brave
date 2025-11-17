import asyncio
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
from brave.api.schemas.analysis import AnalysisInput,Analysis, UpdateProject,QueryAnalysis,AnalysisExecuterModal
from typing import Dict, Any
from brave.api.models.core import analysis,t_container
import json
import importlib
import importlib.util
import uuid
import os
from brave.api.service.result_parse import script_analysis
from brave.api.service.result_parse import nextflow_analysis
from brave.api.service.result_parse.nextflow_analysis    import NextflowAnalysis
from brave.api.service.result_parse.result_parse import ResultParse
from brave.api.utils import file_utils
from brave.api.utils.get_db_utils import get_ids
from brave.api.config.config import get_settings
from brave.api.routes.pipeline import get_pipeline_file
import textwrap
# from brave.api.routes.sample_result import find_analyais_result_by_ids
from brave.api.routes.sample_result import parse_result_one
import  brave.api.service.pipeline as pipeline_service
import brave.api.service.bio_database_service as bio_database_service
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
from brave.api.utils.file_utils import delete_all_in_dir
import  brave.api.service.file_operation  as file_operation_service
import pandas as pd
import brave.api.service.container_service as container_service
import shutil
import brave.api.service.notebook as notebook_service
from brave.api.models.core import t_pipeline_components
from sqlalchemy.orm import aliased
from collections import defaultdict

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
    event_bus:EventBus = Depends(Provide[AppContainer.event_bus]) 
   ):


    resultParse = ResultParse(analysis_id,event_bus)
    
    with get_engine().begin() as conn:
        if save:
            result_list,result_dict,params = await resultParse.parse(True)
            # result = await analysis_result_parse_service.save_analysis_result_preview(conn,analysis_id)
        else:
            # result = await analysis_result_parse_service.parse_analysis_result_preview(conn,analysis_id)
            result_list,result_dict,params = await resultParse.parse(False)

        file_format_list = params["file_format_list"]
        file_dict = analysis_service.get_file_dict(file_format_list,params['analysis']['output_dir'])
        # file_dict = find_file_dict(file_format_list,params['analysis']['output_dir'])   
        # [item for item in result_dict.items()]
        # pd.DataFrame()
        for key,value in result_dict.items():
            df = pd.DataFrame(value)
            result_dict[key] = file_utils.get_table_content_by_df(df)
        analysis= params['analysis']
        return {
            "analysis_id":analysis["analysis_id"],
            "command_log_path":analysis["command_log_path"],
            "job_status":analysis["job_status"],
            "result_dict":result_dict,
            "file_format_list":file_format_list,
            "file_dict":file_dict}


@analysis_api.post(
    "/list-analysis",
    # response_model=List[Analysis],
)
async def list_analysis(query:QueryAnalysis):
    with get_engine().begin() as conn:
        return  analysis_service.list_analysis(conn,query)

def build_tree(data):
    grouped = defaultdict(list)
    for item in data:
        grouped[item["component_id"]].append(item)

    tree = []
    for comp_id, items in grouped.items():
        parent = {
            "title": items[0]["component_name"],  # 每组的名字
            "key": comp_id,   
            "type":"components",                    # 用 component_id 当 key
            "children": []
        }
        for i, it in enumerate(items):
            parent["children"].append({
                "title": it["analysis_name"],
                "type":"analysis",
                "key": it["analysis_id"],
                "component_id": it["component_id"],
                "component_name": it["component_name"],
                "component_type": it["component_type"],
                "job_status": it["job_status"],
                "server_status": it["server_status"],
                "component_order_index": it["component_order_index"]

            })
        tree.append(parent)
    return tree

@analysis_api.post(
    "/list-analysis-tree",
    # response_model=List[Analysis],
)
async def list_analysis(query:QueryAnalysis):
    with get_engine().begin() as conn:
        analysis_list = analysis_service.list_analysis_v1(conn,query)
    analysis_list = [dict(item) for item in analysis_list]
    sorted_data = sorted(
        analysis_list,
        key=lambda x: (
            0 if x["component_order_index"] not in (None, "") else 1,   # 有值优先，空值最后
            -(int(x["component_order_index"])) if x["component_order_index"] not in (None, "") else float("inf")  # 数字取负 → 实现降序
        )
    )
    data = build_tree(sorted_data)
    return data


@analysis_api.delete("/fast-api/analysis/{analysis_id}",  status_code=HTTP_204_NO_CONTENT)
def delete_analysis(analysis_id: str):
    with get_engine().begin() as conn:
        find_analysis = analysis_service.find_analysis_by_id(conn,analysis_id)
        find_analysis_result = analysis_result_service.find_analysis_result_by_analysis_id(conn,analysis_id)
        if find_analysis_result:
            raise HTTPException(status_code=500, detail=f"Existing analysis results cannot be deleted!")
        output_dir = find_analysis.output_dir
        # delete_all_in_dir(output_dir)
        if os.path.exists(output_dir):
            print(f"delete dir: {output_dir}")
            shutil.rmtree(output_dir)
            
        conn.execute(analysis.delete().where(analysis.c.analysis_id == analysis_id))

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
    is_report:Optional[bool]=None,
    app_container:AppContainer = Depends(Provide[AppContainer]),
    evenet_bus:EventBus = Depends(Provide[AppContainer.event_bus])
    ): # request_param: Dict[str, Any]
    

    with get_engine().begin() as conn:
        component_id = request_param['component_id']
        # pipeline_id = request_param['pipeline_id']
        if component_id is None:
            raise HTTPException(status_code=500, detail=f"component_id is None")
        component = pipeline_service.find_pipeline_by_id(conn, component_id)
        if component["component_type"] == "pipeline":
            component = pipeline_service.get_pipeline_v2(conn,component_id)
        if component is None:
            raise HTTPException(status_code=404, detail=f"Component with id {component_id} not found")
        if component is None or "content" not in component:
            raise HTTPException(status_code=404, detail=f"Component with id {component_id} not found or missing content.")
        
        # component_content = 
        component_obj = {
            **{ k:v for k,v in component.items() if k != "content"},
            **json.loads(component['content'])
        }

        script_type = component_obj['script_type']   
        # if  script_type=="nextflow":
        #     analysis_controller = app_container.nextflow_analysis()
        # else:
        #     analysis_controller = app_container.script_analysis()
        

        if script_type == "python" or script_type == "shell" or script_type == "r" or script_type == "jupyter":
            analysis_controller = app_container.script_analysis()
        else:
            analysis_controller = app_container.nextflow_analysis()

        parse_analysis_result = analysis_controller.get_parames(conn,request_param,component_obj)
        if not save:
            return parse_analysis_result
        
        save_analysis = await analysis_controller.save_analysis(conn,request_param,parse_analysis_result,component_obj,is_report) 
        if is_submit:
            analysis_executer_modal = await analysis_service.run_analysis(conn,save_analysis,"job")
            await evenet_bus.dispatch(RoutersName.ANALYSIS_EXECUTER_ROUTER,AnalysisExecutorEvent.ON_ANALYSIS_SUBMITTED,analysis_executer_modal)

        return parse_analysis_result
  


@analysis_api.get("/get-executor-logs/{analysis_id}")
@inject
def get_executor_logs(analysis_id,job_executor_selector:JobExecutor = Depends(Provide[AppContainer.job_executor_selector])):
    return job_executor_selector.get_logs(analysis_id)




@analysis_api.post("/run-analysis-v2/{analysis_id}")
@inject
async def run_analysis_v2(
    analysis_id,
    run_type:str="job",
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
        # await analysis_service.run_analysis(conn,analysis_,run_type,evenet_bus)
        analysis_executer_modal = await analysis_service.run_analysis(conn,analysis_,run_type)
    await evenet_bus.dispatch(RoutersName.ANALYSIS_EXECUTER_ROUTER,AnalysisExecutorEvent.ON_ANALYSIS_SUBMITTED,analysis_executer_modal)

    #     # process_id = analysis_['process_id']
    #     component = pipeline_service.find_component_by_id(conn,analysis_["component_id"])
    #     component_type = component['component_type']
    #     if run_type=="job" and component_type=="script":
    #         output_dir = f"{analysis_['output_dir']}/output"
    #         # if os.path.exists(output_dir):
    #         delete_all_in_dir(output_dir)
        
    #     if not component["container_id"]:
    #         raise HTTPException(status_code=500, detail=f"please config container id") 

    #     # find_container = container_service.find_container_by_id(conn,analysis_["container_id"])
    #     analysis_ = dict(analysis_)
    #     analysis_["run_id"] = f"{run_type}-{analysis_id}"
        
    #     if run_type == "job":
    #         analysis_["container_id"] =component["container_id"]
    #     else:
    #         # if component_type=="script":
    #         analysis_["container_id"] =component["container_id"]
    #         # else: 
    #         #     if not component["sub_container_id"]:
    #         #         raise HTTPException(status_code=500, detail=f"please config sub_container_id id") 
    #         #     analysis_["container_id"] = component["sub_container_id"]

    #     # analysis_["image"] = find_container["image"]
    #     analysis_ = AnalysisExecuterModal(**analysis_)
    #     # analysis_.image = find_container["image"]
    #     await analysis_service.finished_analysis(analysis_id,run_type,"running")
    #     # stmt = analysis.update().values({"analysis_status":"running","run_type":run_type}).where(analysis.c.analysis_id==analysis_id)
    #     # conn.execute(stmt)
    # await evenet_bus.dispatch(RoutersName.ANALYSIS_EXECUTER_ROUTER,AnalysisExecutorEvent.ON_ANALYSIS_SUBMITTED,analysis_)
    
    
    # job_id = await executor.submit_job(LocalJobSpec(
    #     job_id=analysis_id,
    #     command=["bash", "run.sh"],
    #     output_dir=analysis_['output_dir'],
    #     process_id=analysis_['process_id']
    # ))

    return {"msg":"success"}


@analysis_api.post("/analysis/stop-analysis/{analysis_id}")
@inject
async def stop_analysis(
    analysis_id,
    run_type,
    evenet_bus:EventBus = Depends(Provide[AppContainer.event_bus]) 
    ):


    with get_engine().begin() as conn:
        stmt = select(analysis).where(analysis.c.analysis_id == analysis_id)
        result = conn.execute(stmt)
        analysis_ = result.mappings().first()
        if analysis_ is None:
            raise HTTPException(status_code=404, detail="Analysis not found")
        analysis_service.finished_analysis_(conn,analysis_id,run_type,"stopping")

        run_id = f"{run_type}-{analysis_id}"
        analysis_ = AnalysisExecuterModal(**analysis_,run_id=run_id)
        
        # stmt = analysis.update().values({"analysis_status":"running"}).where(analysis.c.analysis_id==analysis_id)
        # conn.execute(stmt)

        asyncio.create_task(evenet_bus.dispatch(RoutersName.ANALYSIS_EXECUTER_ROUTER,AnalysisExecutorEvent.ON_ANALYSIS_STOPED,analysis_))
        
    
        return {"msg":"success"}


@analysis_api.get("/find-analysis-by-id/{analysis_id}") 
async def find_analysis_by_id(analysis_id):
    settings = get_settings()
    with get_engine().begin() as conn:
        t_sub_container = aliased(t_container)

        stmt = select(
            analysis,
            t_container.c.name.label("container_name"),
            t_container.c.image.label("container_image"),
            t_sub_container.c.name.label("sub_container_name"),
            t_sub_container.c.image.label("sub_container_image")
        )

        stmt = stmt.select_from(
                analysis.outerjoin(t_pipeline_components,analysis.c.component_id==t_pipeline_components.c.component_id)
                .outerjoin(t_container,t_pipeline_components.c.container_id==t_container.c.container_id)
                .outerjoin(t_sub_container,t_pipeline_components.c.sub_container_id==t_sub_container.c.container_id)
            #  analysis.outerjoin(t_container, analysis.c.container_id == t_container.c.container_id)
        )
        stmt = stmt.where(analysis.c.analysis_id == analysis_id)
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


def format_form_json_item(item):
    if item.get("type") =='CollectedGroupSelectSampleButton':
        item["type"] = "CollectedSimplpeGroupSelect"
        
    elif item.get("type") =="GroupSelectSampleButton":
        item["type"] = "SimplpeGroupSelect"
    elif item.get("db") and item.get("db")==True:
        item = None
    return item

@analysis_api.get("/analysis/visualization-results/{analysis_id}")
async def visualization_results(analysis_id):
    with get_engine().begin() as conn:
        find_analysis = analysis_service.find_analysis_by_id(conn,analysis_id)
        if not find_analysis:
            raise HTTPException(status_code=404, detail=f"Analysis with id {analysis_id} not found")
        find_component = pipeline_service.find_component_by_id(conn,find_analysis['component_id'])
    file_result = await file_operation_service.visualization_results(find_analysis["output_dir"])
    # file_result = {}
    file_result['description'] = find_component["description"]
    file_result['analysis_name'] = find_analysis["analysis_name"]
    file_result['job_status'] = find_analysis["job_status"]
    file_result['server_status'] = find_analysis["server_status"]
    file_result['is_report'] = find_analysis["is_report"]
    file_result['analysis_id'] = find_analysis["analysis_id"]

    # file_result['analysis_id'] = find_analysis["analysis_id"]

    file_result['component_name'] = find_component["component_name"]
    
    file_result['component_id'] = find_component["component_id"]

    file_result['component_type'] = find_component["component_type"]
    file_result['command_log_path'] = find_analysis["command_log_path"]

    file_result['request_param'] =  json.loads(find_analysis["request_param"])
    
    component_content = json.loads(find_component["content"])
    if "formJson" in component_content:
        form_json = component_content["formJson"]
        
        # if not  item.get("db")
        file_result['form_json'] =  [format_form_json_item(item)  for item in form_json  if item.get("quickShow")!=False and  item.get("name")!="group_field"]
    else:
        file_result['form_json'] = []

    file_result['form_json'] = [item for item in file_result['form_json'] if item is not None]


    return file_result

@analysis_api.get("/analysis/analysis-progress/{analysis_id}")
async def analysis_progress(analysis_id):
    with get_engine().begin() as conn:
        find_analysis = analysis_service.find_analysis_by_id(conn,analysis_id)
    trace_file = find_analysis["trace_file"]
    df = pd.read_csv(trace_file,sep="\t")
    return json.loads(df.to_json(orient="records"))


@analysis_api.post("/analysis/convert-ipynb/{analysis_id}")
async def convert_ipynb(analysis_id):
    with get_engine().begin() as conn:
        find_analysis = analysis_service.find_analysis_by_id(conn,analysis_id)
    script_path  = find_analysis["pipeline_script"]
    ipynb_path = os.path.dirname(script_path)
    ipynb_path = f"{ipynb_path}/main.ipynb"
    if os.path.exists(script_path) and os.path.exists(ipynb_path):
        shutil.copy(script_path, f"{script_path}.tmp")
        notebook_service.convert_notebook(ipynb_path, script_path)
        return "success"
    raise HTTPException(status_code=404, detail=f"{script_path}或{ipynb_path}不存在!")


@analysis_api.post("/analysis/update-report/{analysis_id}")
async def update_report(analysis_id):
    with get_engine().begin() as conn:
        find_analysis = analysis_service.find_analysis_by_id(conn,analysis_id)
        if find_analysis['is_report']:
            analysis_service.update_report(conn,analysis_id,False)
        else:
            analysis_service.update_report(conn,analysis_id,True)
    return "success"


@analysis_api.post("/analysis/edit-params/{analysis_id}")
async def edit_params(analysis_id):
    analysis_result = {}
    inputFormJson = []
    # project = editParams.project if editParams.project else []
    with get_engine().begin() as conn:
        find_analysis = analysis_service.find_analysis_by_id(conn,analysis_id)
        find_component = pipeline_service.find_component_by_id(conn,find_analysis['component_id'])
        project = json.loads(find_analysis["extra_project_ids"]) if "extra_project_ids" in  find_analysis and find_analysis["extra_project_ids"] else []

        request_param = json.loads(find_analysis["request_param"])
        if "data_component_ids" in request_param:
            data_component_ids = request_param["data_component_ids"]
            data_component_ids = json.loads(data_component_ids)
            # find_analysis["project"]
           
            project.append(find_analysis["project"])
            analysis_result = analysis_result_service.find_analyais_result_groupd_by_component_ids(conn,data_component_ids,project)
        
        component_type = find_component["component_type"]
        
        if component_type == "software" or component_type=="pipeline":
            software_input_file = pipeline_service.find_component_by_parent_id(conn,find_component['component_id'],"software_input_file")
            inputFormJson = [
                {
                    # **{k:v for k,v in item.items() if k!="content"},
                    "component_id":item["component_id"],
                    **json.loads(item["content"])
                } for item in software_input_file
            ]

    result = {
        "analysis_name":find_analysis["analysis_name"],
        "is_report":find_analysis["is_report"],
        "analysis_id":find_analysis["analysis_id"],
        "component_name":find_component["component_name"],
        "component_type":find_component["component_type"],
        "component_id":find_component["component_id"],
        "request_param":json.loads(find_analysis["request_param"]),
        "content":json.loads(find_component["content"]),
        "analysis_result":analysis_result,
        "inputFormJson":inputFormJson

    }

    return result


@analysis_api.post("/analysis/update-extra-project/{analysis_id}")
async def edit_params(project:UpdateProject,analysis_id):
    with get_engine().begin() as conn:
        # find_analysis = analysis_service.find_analysis_by_id(conn,analysis_id)
        analysis_service.update_extra_project(conn,analysis_id,project.project)
    return "success"


# @analysis_api.post("/analysis/update-pipeline-dir/{analysis_id}")
# async def update_pipeline_dir(analysis_id):
#     pipline_dir = pipeline_service.get_pipeline_dir()
#     pipline_dir = str(pipline_dir)
#     with get_engine().begin() as conn:
#         analsyis = analysis_service.find_analysis_by_id(conn,analysis_id)
#         analysis_service.update_pipeline_dir(conn,analsyis)
#     return "success"

@analysis_api.post("/analysis/find-analysis-by-component-id/{component_id}")
async def find_analysis_by_component_id(component_id):
    with get_engine().begin() as conn:
        return analysis_service.find_analysis_by_component_id(conn, component_id)  
    
@analysis_api.post("/analysis/update_used/{analysis_id}")
async def update_used(analysis_id: str):
    with get_engine().begin() as conn:
        analysis_service.update_used(conn,analysis_id)
    return "success"
