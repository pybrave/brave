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
from brave.api.schemas.analysis import AnalysisInput,Analysis
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
from brave.api.service.pipeline  import get_all_module

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
    



def parse_analysis(request_param,params_path,command_path,work_dir,module_name):
    all_module = get_all_module("py_parse_analysis")
    if module_name not in all_module:
        raise HTTPException(status_code=500, detail=f"py_parse_analysis: {module_name}没有找到!")
    py_module = all_module[module_name]
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
def save_analysis(request_param: Dict[str, Any]): # request_param: Dict[str, Any]
    # request_param = analysis_input.model_dump_json()
    

    with get_engine().begin() as conn:
        analysis_pipline = request_param['analysis_pipline']

        parse_analysis_module = request_param['parse_analysis_module']
        parse_analysis_result_module = json.dumps(request_param['parse_analysis_result_module'])
        new_analysis = {
            "project":request_param['project'],
            "analysis_name":request_param['analysis_name'],
            "analysis_method":analysis_pipline,
            "request_param":json.dumps(request_param),
            "parse_analysis_module":parse_analysis_module
        }
     
        output_dir=None
        work_dir=None
        result = None
        if "id" in request_param:
            stmt = select(analysis).where(analysis.c.id == request_param['id'])
            result = conn.execute(stmt).fetchone()
        if result:
            output_dir = result.output_dir
            work_dir = result.work_dir
            params_path = result.params_path
            command_path = result.command_path
            parse_analysis(request_param,params_path,command_path, work_dir,parse_analysis_module)
            new_analysis['output_format'] = parse_analysis_result_module
            stmt = analysis.update().values(new_analysis).where(analysis.c.id==request_param['id'])
        else:
            settings = get_settings()
            base_dir = settings.BASE_DIR
            work_dir = settings.WORK_DIR
            str_uuid = str(uuid.uuid4())
            # /ssd1/wy/workspace2/nextflow_workspace
            wrap_analysis_pipline = ""
            if 'wrap_analysis_pipeline' in request_param:
                wrap_analysis_pipline = request_param['wrap_analysis_pipeline']+"/"

            output_dir = f"{base_dir}/{request_param['project']}/{wrap_analysis_pipline}{analysis_pipline}"
            # /data/wangyang/nf_work/
            work_dir = f"{work_dir}/{request_param['project']}/{wrap_analysis_pipline}{analysis_pipline}"
            params_path = f"{output_dir}/params.json"
            command_path= f"{output_dir}/run.sh"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            if not os.path.exists(work_dir):
                os.makedirs(work_dir)
            # 写入脚本

            script =  f"{get_pipeline_file(analysis_pipline)}"
            new_analysis['pipeline_script'] = script

            command =  textwrap.dedent(f"""
            nextflow run -offline -resume  \\
                {script} \\
                -params-file {params_path} \\
                -w {work_dir} \\
                -with-trace trace.txt | tee .workflow.log
            """)
            with open(command_path, "w") as f:
                f.write(command)
            

            new_analysis['work_dir'] = work_dir
            new_analysis['output_dir'] = output_dir
            new_analysis['params_path'] = params_path
            new_analysis['command_path'] = command_path
            new_analysis['analysis_key'] = str_uuid

            parse_analysis(request_param,params_path, command_path,work_dir,parse_analysis_module)
            new_analysis['output_format'] = parse_analysis_result_module
      
            stmt = analysis.insert().values(new_analysis)
        conn.execute(stmt)
        
       
        

        # print()
        # return conn.execute(samples.select()).fetchall()
        # print()
    return {"msg":"success"}


@analysis_api.get(
    "/fast-api/analysis",
    response_model=List[Analysis],
)
def get_analysis(analysis_method,project):
    with get_engine().begin() as conn:
        return conn.execute(analysis.select().where(
            and_(analysis.c.analysis_method==analysis_method,
            analysis.c.project==project,
            )
        )).fetchall()


@analysis_api.delete("/fast-api/analysis/{id}",  status_code=HTTP_204_NO_CONTENT)
def delete_user(id: int):
    with get_engine().begin() as conn:
        conn.execute(analysis.delete().where(analysis.c.id == id))
    return {"message":"success"}


@analysis_api.post("/fast-api/parse-analysis-result/{id}")
def parse_analysis_result(id):
    with get_engine().begin() as conn:
        stmt = select(analysis).where(analysis.c.id == id)
        result = conn.execute(stmt).fetchone()
    output_format = json.loads(result.output_format)
    if len(output_format)==0:
        raise HTTPException(status_code=500, detail=f"分析{result.analysis_method}没有配置output_format!")
    for item in output_format:
        dir_path = f"{result.output_dir}/output/{item['dir']}"
        all_module = get_all_module("py_parse_analysis_result")
        if item['module'] not in all_module:
            raise HTTPException(status_code=500, detail=f"py_parse_analysis_result: {module_name}没有找到!")
        py_module = all_module[item['module']]
        module = importlib.import_module(py_module)
        # parse_result_one()
        moduleArgs = {}
        if "moduleArgs" in item:
            moduleArgs = item['moduleArgs']
        parse_result_oneV2(item['analysisMethod'],moduleArgs,result,module,dir_path,result.project,"V1.0",id)
    return {"message":"success"}