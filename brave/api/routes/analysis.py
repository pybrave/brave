from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
# from brave.api.config.db import conn
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
from brave.api.schemas.analysis import AnalysisInput,Analysis,QueryAnalysis
from typing import Dict, Any
from brave.api.models.core import analysis
import json
import importlib
import importlib.util
import uuid
import os
from brave.api.utils.get_db_utils import get_ids
from brave.api.config.config import get_settings
from brave.api.routes.pipeline import get_pipeline_file
import textwrap
from brave.api.routes.sample_result import find_analyais_result_by_ids
from brave.api.routes.sample_result import parse_result_one,parse_result_oneV2
from brave.api.service.pipeline  import get_all_module,find_module
import  brave.api.service.pipeline as pipeline_service
import inspect
from typing import Optional
import pandas as pd
import subprocess
from brave.api.service.watch_service import queue_process
import threading
import psutil
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
    



def parse_analysis(request_param,params_path,command_path,work_dir,module_name,component_id):
    # all_module = get_all_module("py_parse_analysis")
    # if module_name not in all_module:
    #     raise HTTPException(status_code=500, detail=f"py_parse_analysis: {module_name}没有找到!")
    # py_module = all_module[module_name]

  
    py_module = find_module("py_parse_analysis",component_id,module_name)['module']

    # module_name = f'brave.api.parse_analysis.{module_name}'
    # if importlib.util.find_spec(module) is None:
    #     print(f"{module_name}不存在!")
    # else:
    module = importlib.import_module(py_module)
    get_db_field = getattr(module, "get_db_field")
    db_field = get_db_field()

    db_ids_dict = {key: get_ids(request_param[key]) for key in db_field if key in request_param}
    # with get_db_session() as session:
        # get_db_value
    db_dict = { key:find_analyais_result_by_ids(value) for key,value in  db_ids_dict.items()}
    parse_data = getattr(module, "parse_data")

    result = parse_data(request_param,db_dict)
    with open(params_path, "w") as f:
        json.dump(result,f)

        # get_script = getattr(module, "get_script")
        # script = get_script()
        # command = f"nextflow run -offline {script} -resume  -params-file {params_path} -w {work_dir} -with-trace trace.txt | tee .workflow.log"
        # with open(command_path, "w") as f:
        #     f.write(command)
        # get_output_format = getattr(module, "get_output_format")
        # output_format = get_output_format()
        # return json.dumps(output_format)

# ,response_model=List[Sample]
@analysis_api.post("/fast-api/save-analysis")
async def save_analysis(request_param: Dict[str, Any]): # request_param: Dict[str, Any]
    # request_param = analysis_input.model_dump_json()
    component_id = request_param['component_id']
    pipeline_id = request_param['pipeline_id']


    with get_engine().begin() as conn:
        component = pipeline_service.find_pipeline_by_id(conn, component_id)
        if component is None or not hasattr(component, "content"):
            raise HTTPException(status_code=404, detail=f"Component with id {component_id} not found or missing content.")
        component_content = json.loads(component.content)
        parse_analysis_module = component_content.get('parseAnalysisModule')
        if parse_analysis_module is None:
            raise HTTPException(status_code=500, detail=f"'parseAnalysisModule' not found in component content.")
        # component_script = component_content.get('analysisPipline') # 分析脚本
        # parse_analysis_module = request_param.get('parse_analysis_module')
        # parse_analysis_result_module = json.dumps(request_param.get('parse_analysis_result_module'))
        new_analysis = {
            "project":request_param['project'],
            "analysis_name":request_param['analysis_name'],
            "request_param":json.dumps(request_param),
            # "analysis_method":component_script,
            "component_id":component_id
            # "parse_analysis_module":parse_analysis_module
        }
        # module_dir = pipeline_id
        # if "moduleDir" in component_content:
        #     module_dir = component_content['moduleDir']

        output_dir=None
        work_dir=None
        result = None
        if "id" in request_param:
            stmt = select(analysis).where(analysis.c.id == request_param['id'])
            result = conn.execute(stmt).fetchone()
        if result:
            output_dir = result.output_dir
            work_dir = result.work_dir
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            if not os.path.exists(work_dir):
                os.makedirs(work_dir)
            params_path = result.params_path
            command_path = result.command_path
            parse_analysis(request_param,params_path,command_path, work_dir,parse_analysis_module,component_id)
            # new_analysis['output_format'] = parse_analysis_result_module
            stmt = analysis.update().values(new_analysis).where(analysis.c.id==request_param['id'])
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
            output_dir = f"{project_dir}/{pipeline_id}/{component_id}/{str_uuid}"
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
            component_script = find_module("nextflow",component_id,None)['path']

            # pipeline_script =  f"{get_pipeline_file(pipeline_script)}"
            new_analysis['pipeline_script'] = component_script

            command =  textwrap.dedent(f"""
            export NXF_CACHE_DIR={cache_dir}
            nextflow -log {executor_log} run -offline -resume  \\
                -ansi-log false \\
                {component_script} \\
                -params-file {params_path} \\
                -w {work_dir} \\
                -with-trace {trace_file} | tee {workflow_log_file}
            """)
            with open(command_path, "w") as f:
                f.write(command)
            
            
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

            parse_analysis(request_param,params_path, command_path,work_dir,parse_analysis_module,component_id)
            # new_analysis['output_format'] = parse_analysis_result_module
      
            stmt = analysis.insert().values(new_analysis)
        conn.execute(stmt)
        
       
        

        # print()
        # return conn.execute(samples.select()).fetchall()
        # print()
    return {"msg":"success"}


@analysis_api.post(
    "/list-analysis",
    response_model=List[Analysis],
)
async def list_analysis(query:QueryAnalysis):
    conditions = []
    if query.analysis_id:
        conditions.append(analysis.c.analysis_id == query.analysis_id)
    if query.analysis_method:
        conditions.append(analysis.c.analysis_method == query.analysis_method)
    if query.component_id:
        conditions.append(analysis.c.component_id == query.component_id)
    if query.project:
        conditions.append(analysis.c.project == query.project)

    stmt = select(analysis)
    if conditions:
        stmt = stmt.where(and_(*conditions))
    with get_engine().begin() as conn:
        return conn.execute(stmt).fetchall()


@analysis_api.delete("/fast-api/analysis/{id}",  status_code=HTTP_204_NO_CONTENT)
def delete_user(id: int):
    with get_engine().begin() as conn:
        conn.execute(analysis.delete().where(analysis.c.id == id))
    return {"message":"success"}




def get_all_files_recursive(directory,dir_name,file_dict):
    file_list=[]
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file).replace(directory,""))
    return file_dict.update({dir_name:file_list})

@analysis_api.post("/fast-api/parse-analysis-result/{analysis_id}")
async def parse_analysis_result(analysis_id,save:Optional[bool]=False):
    with get_engine().begin() as conn:
        stmt = select(analysis).where(analysis.c.analysis_id == analysis_id)
        result = conn.execute(stmt).fetchone()
        component_id = result.component_id
        component_ = pipeline_service.find_pipeline_by_id(conn,component_id)
    # output_format = json.loads(pipeline_.output_format)
    pipeline_content = json.loads(component_.content)
    output_format = pipeline_content['parseAnalysisResultModule']
    if len(output_format)==0:
        raise HTTPException(status_code=500, detail=f"组件{component_id}没有配置output_format!")
    result_dict = {}
    file_dict={}
    for item in output_format:

        dir_path = f"{result.output_dir}/output/{item['dir']}"
        # module_dir = component_.pipeline_key
        # if "moduleDir" in pipeline_content:
        #     module_dir = pipeline_content['moduleDir']
        # 递归获取dir_path的文件
     
     

        get_all_files_recursive(dir_path,item['dir'],file_dict)

        py_module = find_module("py_parse_analysis_result",component_id,item['module'])['module']

        # all_module = get_all_module("py_parse_analysis_result")
        # if item['module'] not in all_module:
        #     raise HTTPException(status_code=500, detail=f"py_parse_analysis_result: {module_name}没有找到!")
        # py_module = all_module[]
        module = importlib.import_module(py_module)
        # parse_result_one()
        moduleArgs = {}
        if "moduleArgs" in item:
            moduleArgs = item['moduleArgs']
        
        parse = getattr(module, "parse")
        sig = inspect.signature(parse)
        params = sig.parameters
        res = None    
        args = {
            "dir_path":dir_path,
            "analysis": result,
            **moduleArgs
        }
        res = parse(**args)
        result_dict.update({item['module']:res})
        if save:
            parse_result_oneV2(res,item['analysisMethod'],result.project,"V1.0",analysis_id)
    return {
        "result_dict":result_dict,
        "file_dict":file_dict
    }



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
async def run_analysis(analysis_id):
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
        stmt = analysis.update().values({"process_id":pid}).where(analysis.c.analysis_id==analysis_id)
        conn.execute(stmt)
    analysis_dict = dict(analysis_)

    analysis_dict['process_id'] = pid
    await queue_process.put(analysis_dict)
    return {"pid":pid}

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