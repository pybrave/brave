from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
import threading

# from brave.api.config.db import conn
# from models.user import users
from typing import List
from starlette.status import HTTP_204_NO_CONTENT
from sqlalchemy import func, select
from brave.api.models.orm import SampleAnalysisResult
import glob
import importlib
import os
import json
from brave.api.config.db import get_db_session
from sqlalchemy import and_,or_
from brave.api.schemas.analysis_result import AnalysisResultQuery,AnalysisResult
from brave.api.models.core import samples,analysis_result
from brave.api.config.db import get_engine
import inspect
from fastapi import HTTPException
from brave.api.service.pipeline  import get_all_module,get_pipeline_dir
import threading
import brave.api.service.analysis_result_service as analysis_result_service

sample_result = APIRouter()
# key = Fernet.generate_key()
# f = Fernet(key)


# def get_all_subclasses(cls):
#     subclasses = set(cls.__subclasses__())
#     for subclass in subclasses.copy():
#         subclasses.update(get_all_subclasses(subclass))
#     return subclasses




def update_or_save_result(analysis_key,sample_name, software, content_type, content, db, project, verison, analysis_method,analysis_name,analysis_id):
        sampleAnalysisResult = db.query(SampleAnalysisResult) \
        .filter(and_(SampleAnalysisResult.analysis_method == analysis_method,\
                SampleAnalysisResult.analysis_version == verison, \
                SampleAnalysisResult.analysis_key == analysis_key, \
                SampleAnalysisResult.project == project \
            )).first()
        if sampleAnalysisResult:
            sampleAnalysisResult.sample_name = sample_name
            sampleAnalysisResult.content = content
            sampleAnalysisResult.sample_key=sample_name
            sampleAnalysisResult.content_type = content_type
            sampleAnalysisResult.analysis_name = analysis_name
            sampleAnalysisResult.analysis_id = analysis_id
            sampleAnalysisResult.analysis_type="upstream"
            # sampleAnalysisResult.log_path = log_path
            sampleAnalysisResult.software = software
            db.commit()
            db.refresh(sampleAnalysisResult)
            print(">>>>更新: ",sample_name, software, content_type)
        else:
            sampleAnalysisResult = SampleAnalysisResult(analysis_method=analysis_method, \
                analysis_version=verison, \
                sample_name=sample_name, \
                content_type=content_type, \
                analysis_name=analysis_name, \
                analysis_key=analysis_key, \
                analysis_id=analysis_id, \
                analysis_type="upstream", \
                # log_path=log_path, \
                software=software, \
                project=project, \
                sample_key=sample_name, \
                content=content \
                    )
            db.add(sampleAnalysisResult)
            db.commit()
            print(">>>>新增: ",sample_name, software, content_type)

def parse_result_oneV2(res, analysis_method,project,verison,analysis_id):
    

    # if hasattr(module,"get_analysis_method"):
    #     get_analysis_method = getattr(module, "get_analysis_method")
    #     analysis_method = get_analysis_method()
    #     print(f">>>>>更改分析名称: {analysis_method}")
    analysis_name = analysis_method
    # if hasattr(module,"get_analysis_name"):
    #     get_analysis_name = getattr(module, "get_analysis_name")
    #     analysis_name = get_analysis_name()
        
    with get_db_session() as db:
        if len(res) >0:
            # print(res[0])
            if len(res[0]) == 4:
                for analysis_key,software,content_type,content in res:
                    update_or_save_result(analysis_key,analysis_key, software, content_type, content, db, project, verison, analysis_method,analysis_name,analysis_id)
            elif len(res[0]) == 5:
                for analysis_key,sample_name,software,content_type,content in res:
                    update_or_save_result(analysis_key,sample_name, software, content_type, content, db, project, verison, analysis_method,analysis_name,analysis_id)


def parse_result_one(analysis_method,module,dir_path,project,verison,analysis_id=-1):
    parse = getattr(module, "parse")
    res = parse(dir_path)
    if hasattr(module,"get_analysis_method"):
        get_analysis_method = getattr(module, "get_analysis_method")
        analysis_method = get_analysis_method()
        print(f">>>>>更改分析名称: {analysis_method}")
    analysis_name = analysis_method
    if hasattr(module,"get_analysis_name"):
        get_analysis_name = getattr(module, "get_analysis_name")
        analysis_name = get_analysis_name()
        
    with get_db_session() as db:
        if len(res) >0:
            # print(res[0])
            if len(res[0]) == 4:
                for analysis_key,software,content_type,content in res:
                    update_or_save_result(analysis_key,analysis_key, software, content_type, content, db, project, verison, analysis_method,analysis_name,analysis_id)
            elif len(res[0]) == 5:
                for analysis_key,sample_name,software,content_type,content in res:
                    update_or_save_result(analysis_key,sample_name, software, content_type, content, db, project, verison, analysis_method,analysis_name,analysis_id)
            # print(sample_name)

def parse_result(dir_path,project,verison):
    # pipeline_dir = get_pipeline_dir()
    # py_files = [f for f in os.listdir(f"{pipeline_dir}/*/py_sample_result_parse/*") if f.endswith('.py')]
    # py_files = glob.glob(f"{pipeline_dir}/*/py_sample_result_parse/*.py")
    py_files ={} # get_all_module("py_sample_result_parse")
    for key,py_module in py_files.items():
        # module_name = py_file[:-3]  # 去掉 `.py` 后缀，获取模块名

       
        # if module_name not in all_module:
        #     raise HTTPException(status_code=500, detail=f"py_sample_result_parse: {module_name}没有找到!")
        # py_module = all_module[module_name]
        module = importlib.import_module(py_module)
        support_analysis_method = getattr(module, "support_analysis_method")
        analysis_method = support_analysis_method()

        
        if dir_path.endswith(analysis_method):
            print(f">>>>>找到分析名称 {analysis_method} 的分析结果")
            parse_result_one(analysis_method,module,dir_path,project,verison)
            # parse = getattr(module, "parse")
            # res = parse(dir_path)
            # if hasattr(module,"get_analysis_method"):
            #     get_analysis_method = getattr(module, "get_analysis_method")
            #     analysis_method = get_analysis_method()
            #     print(f">>>>>更改分析名称: {analysis_method}")
            # analysis_name = analysis_method
            # if hasattr(module,"get_analysis_name"):
            #     get_analysis_name = getattr(module, "get_analysis_name")
            #     analysis_name = get_analysis_name()
             
            # with get_db_session() as db:
            #     if len(res) >0:
            #         # print(res[0])
            #         if len(res[0]) == 4:
            #             for analysis_key,software,content_type,content in res:
            #                 update_or_save_result(analysis_key,analysis_key, software, content_type, content, db, project, verison, analysis_method,analysis_name)
            #         elif len(res[0]) == 5:
            #              for analysis_key,sample_name,software,content_type,content in res:
            #                 update_or_save_result(analysis_key,sample_name, software, content_type, content, db, project, verison, analysis_method,analysis_name)
            #         # print(sample_name)


@sample_result.get("/sample-parse-result-test-hexiaoyan",tags=['analsyis_result'])
async def parse_result_restful():
    # base_path ="/ssd1/wy/workspace2/test/test_workspace/result/V1.0"
    # verison = "V1.0"
    # project="test"
    base_path ="/ssd1/wy/workspace2/hexiaoyan/hexiaoyan_workspace2/output"
    verison = "V1.0"
    project="hexiaoyan"
    
    dir_list = glob.glob(f"{base_path}/*",recursive=True)
    for dir_path in dir_list:
        parse_result(dir_path,project,verison)
    return {"msg":"success"}

@sample_result.get("/sample-parse-result-test",tags=['analsyis_result'])
async def parse_result_restful():
    # base_path ="/ssd1/wy/workspace2/test/test_workspace/result/V1.0"
    # verison = "V1.0"
    # project="test"
    base_path ="/ssd1/wy/workspace2/leipu/leipu_workspace2/output"
    verison = "V1.0"
    project="leipu"
    
    dir_list = glob.glob(f"{base_path}/*",recursive=True)
    for dir_path in dir_list:
        parse_result(dir_path,project,verison)
    return {"msg":"success"}

@sample_result.get("/sample-parse-result-test-leipu-meta",tags=['analsyis_result'])
async def parse_result_restful():
    # base_path ="/ssd1/wy/workspace2/test/test_workspace/result/V1.0"
    # verison = "V1.0"
    # project="test"
    base_path ="/ssd1/wy/workspace2/leipu/leipu_workspace_meta/output"
    verison = "V1.0"
    project="leipu"
    
    dir_list = glob.glob(f"{base_path}/*",recursive=True)
    for dir_path in dir_list:
        parse_result(dir_path,project,verison)
    return {"msg":"success"}

@sample_result.get("/sample-parse-result")
async def parse_result_restful(base_path,verison,project):
    # base_path ="/ssd1/wy/workspace2/test/test_workspace/result"
    # verison = "V1.0"
    
    dir_list = glob.glob(f"{base_path}/{verison}/*",recursive=True)
    for dir_path in dir_list:
        parse_result(dir_path,project,verison)
    return {"msg":"success"}

def find_analyais_result_by_ids( value):
    with get_engine().begin() as conn:
        result_dict = analysis_result_service.find_analyais_result_by_ids(conn,value)
    return result_dict

def find_analyais_result(analysisResultQuery:AnalysisResultQuery):
    with get_engine().begin() as conn:
        result_dict = analysis_result_service.find_analyais_result(conn,analysisResultQuery)
    return result_dict

@sample_result.post(
    "/fast-api/find-analyais-result-by-analysis-method",
    response_model=List[AnalysisResult])
async def find_analyais_result_by_analysis_method(analysisResultQuery:AnalysisResultQuery):
    return find_analyais_result(analysisResultQuery)
    # with get_db_session() as session:
    #     analysis_result =  session.query(SampleAnalysisResult,Sample) \
    #         .outerjoin(Sample, SampleAnalysisResult.sample_key == Sample.sample_key) \
    #         .filter(and_( \
    #             SampleAnalysisResult.analysis_method.in_(analysisResultQuery.analysis_method), \
    #             SampleAnalysisResult.project == analysisResultQuery.project \
    #         )) \
    #             .all()

    #     for item in analysis_result:
    #         if item.content_type=="json":
    #             item.content = json.loads(item.content)
            # print()
    # print(f"find_analyais_result_by_analysis_method 当前线程：{threading.current_thread().name}")
  
    # return {"aa":"aa"}


@sample_result.delete("/analyais-result/delete-by-id/{id}",  status_code=HTTP_204_NO_CONTENT)
async def delete_analysis_result(id: int):
    with get_engine().begin() as conn:
        conn.execute(analysis_result.delete().where(analysis_result.c.id == id))
    return {"message":"success"}



@sample_result.post(
    "/fast-api/add-sample-analysis",
    tags=['analsyis_result'],
    description="根据项目名称导入样本")
async def add_sample_analysis(project):
    insert_sample_list = []
    with get_engine().begin() as conn:
        stmt = samples.select().where(samples.c.project==project)
        result  = conn.execute(stmt).fetchall()
        sample_list = [dict(row._mapping) for row in result]
        # sample_list = sample_list[1:2]
        
        for item in sample_list:
            insert_sample_list.append({
                "sample_key":item['sample_key'],
                "sample_name":item['sample_name'],
                "analysis_method":f"V1_{item['sample_composition']}_{item['sequencing_technique']}_{item['sequencing_target']}",
                "content":json.dumps({
                    "fastq1":item['fastq1'],
                    "fastq2":item['fastq2']
                }),
                "project":item['project'],
                "content_type":"json",
            })
    with get_db_session() as db:
        for item in insert_sample_list:
            analysisResult = db.query(SampleAnalysisResult) \
                    .filter(and_(SampleAnalysisResult.sample_key == item['sample_key'], \
                        SampleAnalysisResult.analysis_method == item['analysis_method'] \
                        )).first()
            if analysisResult:
                analysisResult.sample_name = item['sample_name']
                analysisResult.analysis_method = item['analysis_method']
                analysisResult.content = item['content']
                analysisResult.project = item['project']
                analysisResult.content_type = item['content_type']
            else:
                analysisResult = SampleAnalysisResult(**item)
                db.add(analysisResult)
            db.commit()
            db.refresh(analysisResult)

        return {"message":"success"}


