from functools import reduce
from random import sample
import uuid
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
from brave.api.schemas.analysis_result import AnalysisResultQuery,AnalysisResult, ImportData, ParseImportData,UpdateAnalysisResult,BindSample
from brave.api.models.core import samples,analysis_result
from brave.api.config.db import get_engine
import inspect
from fastapi import HTTPException
from brave.api.service.pipeline  import get_default_module, get_all_module,get_pipeline_dir
import threading
import brave.api.service.analysis_result_service as analysis_result_service
import brave.api.service.pipeline as pipeline_service
import re
from brave.api.utils.from_glob_get_file import from_glob_get_file
from brave.api.schemas.sample import AddSampleMetadata,UpdateSampleMetadata
import brave.api.service.sample_service as sample_service
from brave.api.service.analysis_result_parse import AnalysisResultParse
from fastapi import Depends
from dependency_injector.wiring import inject, Provide
from brave.app_container import AppContainer
from collections import defaultdict
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
async def parse_result_restful_test1():
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
async def parse_result_restful_test2():
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
async def parse_result_restful_test3():
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

# def find_analyais_result_by_ids( value):
#     with get_engine().begin() as conn:
#         result_dict = analysis_result_service.find_analyais_result_by_ids(conn,value)
#     return result_dict

def find_analyais_result(analysisResultQuery:AnalysisResultQuery):
    with get_engine().begin() as conn:
        result_dict = analysis_result_service.find_analyais_result(conn,analysisResultQuery)
    return result_dict

def get_analysis_result_metadata(item):
    if item["metadata"]:
        metadata = json.loads(item["metadata"])
        prefix = ""
        if item["sample_source"]:
            prefix = f"{item['sample_source']}-"
        metadata = {k:f"{prefix}{v}" for k,v in metadata.items() if v is not None}
        item = {**metadata,**item}
        del item["metadata"]
    return item
@sample_result.post(
    "/analysis-result/list-analysis-result",
    # response_model=List[AnalysisResult]
    )
async def list_analysis_result(analysisResultQuery:AnalysisResultQuery):
    result_dict = find_analyais_result(analysisResultQuery)
    result_dict = [get_analysis_result_metadata(item) for item in result_dict]
            
        # if item["metadata_form"]:
        #     item["metadata_form"] = json.loads(item["metadata_form"])
    # grouped = defaultdict(list)
    # for item in result_dict:
    #     grouped[item["component_id"]].append(item)
    return result_dict

@sample_result.post(
    "/analysis-result/list-analysis-result-grouped",
    # response_model=List[AnalysisResult]
    )
async def list_analysis_result(analysisResultQuery:AnalysisResultQuery):
    result_dict = find_analyais_result(analysisResultQuery)
    result_dict = [get_analysis_result_metadata(item) for item in result_dict]
            
        # if item["metadata_form"]:
        #     item["metadata_form"] = json.loads(item["metadata_form"])
    grouped = defaultdict(list)
    for item in result_dict:
        item["label"] = item["sample_name"]
        item["value"] = item["id"]
        grouped[item["component_id"]].append(item)
    return grouped


@sample_result.post(
    "/fast-api/find-analyais-result-by-analysis-method",
    # response_model=List[AnalysisResult]
    )
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


@sample_result.delete(
    "/analyais-result/delete-by-id/{analysis_result_id}",  
    status_code=HTTP_204_NO_CONTENT)
@inject
async def delete_analysis_result(
    analysis_result_id: str,
    analysis_result_parse_service:AnalysisResultParse = Depends(Provide[AppContainer.analysis_result_parse_service])):

    with get_engine().begin() as conn:
        find_analysis_result = analysis_result_service.find_by_analysis_result_id(conn,analysis_result_id)
        if not find_analysis_result:
            raise HTTPException(status_code=500, detail=f"分析结果{analysis_result_id}不存在!")
        analysis_id = find_analysis_result.analysis_id
        conn.execute(analysis_result.delete().where(analysis_result.c.analysis_result_id == analysis_result_id))
        analysis_result_parse_service.remove_analysis_result_by_analsyis_result_id(analysis_id,analysis_result_id)
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

    # component_id:str
    # project: str
    # analysis_method: str
    # content: str
    # analysis_key: str


@sample_result.post("/import-data",tags=['analsyis_result'])
async def import_data(importDataList:List[ImportData]):
    with get_engine().begin() as conn:
        for importData in importDataList:
            if not importData.file_name:
                importData.file_name = importData.sample_name
                
            find_sample = sample_service.find_by_sample_name_and_project(conn,importData.sample_name,importData.project)
            sample_id = None
            if  find_sample:
                sample_id = find_sample.sample_id    
            else:
                sample_id = str(uuid.uuid4())
                sample_service.add_sample(conn,{"sample_name":importData.sample_name,"sample_id":sample_id,"project":importData.project}) 
            

            stmt = analysis_result.select().where(and_(
                analysis_result.c.sample_id==sample_id,
                analysis_result.c.component_id==importData.component_id,
                analysis_result.c.project==importData.project,
                analysis_result.c.sample_source==importData.sample_source
            ))
            result = conn.execute(stmt).fetchall()
            if result:
                raise HTTPException(status_code=500, detail=f"分析结果{importData.sample_name}已存在!")

            analysis_result_id = str(uuid.uuid4())
            stmt = analysis_result.insert().values(
                component_id=importData.component_id,
                project=importData.project,
                # analysis_method=analysis_method,
                content=importData.content,
                sample_id=sample_id,
                analysis_result_id=analysis_result_id,
                file_name=importData.file_name,
                sample_source=importData.sample_source,
                # sample_name=importData.sample_name,
                # sample_name=analysis_label,
                content_type="json",
                analysis_type="import_data"
            )
            conn.execute(stmt)
    return {"message":"success"}





@sample_result.post("/parse-import-data",tags=['analsyis_result'])
async def parse_import_data(parseImportData:ParseImportData):

    content = parseImportData.content
    content = json.loads(content)
    result = from_glob_get_file(content)
    # for item in result:
    #     item['file_name'] = item['analysis_key']
    return result

@sample_result.post("/analysis-result/update-analsyis-result",tags=['analsyis_result'])
def update_analsyis_result(updateAnalysisResult:UpdateAnalysisResult):
    with get_engine().begin() as conn:
        stmt = analysis_result.update() 
        stmt = stmt.where(analysis_result.c.id==updateAnalysisResult.id)
        stmt = stmt.values(updateAnalysisResult.model_dump())
        conn.execute(stmt)
        conn.commit()
    return {"message":"success"}


@sample_result.post("/sample/add-sample-metadata",tags=['sample'])
async def add_sample_metadata(sample_metadata:AddSampleMetadata ):
    with get_engine().begin() as conn:
        sample_id = str(uuid.uuid4())
        data = {k:v for k,v in sample_metadata.model_dump().items() if v is not None and k!="sample_id" and k!="analysis_result_id"}

        if sample_metadata.analysis_result_id:
            analysis_result = analysis_result_service.find_by_analysis_result_id(conn,sample_metadata.analysis_result_id)
            if not analysis_result:
                raise HTTPException(status_code=500, detail=f"分析结果{sample_metadata.analysis_result_id}不存在!")
    
            stmt = samples.select().where(samples.c.sample_id==analysis_result.sample_id)
            result = conn.execute(stmt).mappings().first()
            if result:
                raise HTTPException(status_code=500, detail=f"样本metadata{result.sample_id}已存在!")
            analysis_result_service.update_sample_id(conn,sample_metadata.analysis_result_id,sample_id)
            data["project"] = analysis_result.project

        if not sample_metadata.project:
            raise HTTPException(status_code=500, detail=f"项目不能为空!")
        
        data["sample_id"] = sample_id
        stmt = samples.insert().values(data)
        conn.execute(stmt)

    return {"message":"success"}

@sample_result.post("/sample/update-sample-metadata",tags=['sample'])
async def update_sample_metadata(sample_metadata:UpdateSampleMetadata    ):
    data = sample_metadata.model_dump()
    data = {k:v for k,v in data.items() if v is not None and k!="sample_id" }
    with get_engine().begin() as conn:
        stmt = samples.update().where(samples.c.sample_id==sample_metadata.sample_id).values(data)
        conn.execute(stmt)
        conn.commit()
    return {"message":"success"}

@sample_result.post("/sample/update-sample-metadata-list",tags=['sample'])
async def update_sample_metadata(sample_metadata_list:list[UpdateSampleMetadata]):
    for sample_metadata in sample_metadata_list:
        data = sample_metadata.model_dump()
        data = {k:v for k,v in data.items() if v is not None and k!="sample_id" }
        with get_engine().begin() as conn:
            stmt = samples.update().where(samples.c.sample_id==sample_metadata.sample_id).values(data)
            conn.execute(stmt)
            # conn.commit()
    return {"message":"success"}
@sample_result.get("/sample/find-sample-metadata-by-id/{sample_id}",tags=['sample'])
async def find_sample_metadata_by_id(sample_id:str):
    with get_engine().begin() as conn:
        stmt = samples.select().where(samples.c.sample_id==sample_id)
        result = conn.execute(stmt).mappings().first()
    return result


@sample_result.delete("/sample/delete-sample-by-sample-id/{sample_id}",tags=['sample'])
async def delete_sample_by_sample_id(sample_id:str):
    with get_engine().begin() as conn:
        stmt = samples.delete().where(samples.c.sample_id==sample_id)
        conn.execute(stmt)
        conn.commit()
    return {"message":"success"}


@sample_result.post("/sample/bind-sample-to-analysis-result",tags=['sample'])
async def bind_sample_to_analysis_result(bindSample:BindSample):
    with get_engine().begin() as conn:
        stmt = samples.select().where(samples.c.sample_id==bindSample.sample_id)
        result = conn.execute(stmt).mappings().first()
        if not result:
            raise HTTPException(status_code=500, detail=f"样本metadata{bindSample.sample_id}不存在!")
        analysis_result = analysis_result_service.find_by_analysis_result_id(conn,bindSample.analysis_result_id)
        if not analysis_result:
            raise HTTPException(status_code=500, detail=f"分析结果{bindSample.analysis_result_id}不存在!")
        analysis_result_service.update_sample_id(conn,bindSample.analysis_result_id,bindSample.sample_id)
    return {"message":"success"}