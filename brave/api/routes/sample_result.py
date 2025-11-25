from functools import reduce
from random import sample
import shutil
import uuid
from fastapi import APIRouter,Depends, File, Form, UploadFile
import pandas as pd
from sqlalchemy.orm import Session
import threading

# from brave.api.config.db import conn
# from models.user import users
from typing import List
from starlette.status import HTTP_204_NO_CONTENT
from sqlalchemy import func, select,insert
from brave.api.config.config import get_settings
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
from brave.api.utils import file_utils
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

@sample_result.get("/analysis-result/table/{analysis_result_id}",)
def get_analysis_result_table(analysis_result_id,row_num=-1):
    with get_engine().begin() as conn:
        result_one = analysis_result_service.find_by_analysis_result_id(conn,analysis_result_id)
        content = file_utils.get_table_content(result_one["content"],row_num)
    return content





def get_analysis_result_metadata(item):
    if item["metadata"]:
        metadata = json.loads(item["metadata"])
        # prefix = ""
        # if item["sample_source"]:
        #     prefix = f"{item['sample_source']}-"
        metadata = {k:f"{v}" for k,v in metadata.items() if v is not None}
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
    
    with get_engine().begin() as conn:
        grouped =  analysis_result_service.find_analysis_result_grouped(conn,analysisResultQuery)

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
            
            if importData.file_type !="collected":
                # find_sample = sample_service.find_by_sample_name_and_project(conn,importData.sample_name,importData.project)
                # sample_id = None
                # if  find_sample:
                #     sample_id = find_sample.sample_id    
                # else:
                #     sample_id = str(uuid.uuid4())
                #     sample_service.add_sample(conn,{"sample_name":importData.sample_name,"sample_id":sample_id,"project":importData.project}) 
                
                stmt = analysis_result.select().where(and_(
                    analysis_result.c.file_name==importData.file_name,
                    analysis_result.c.component_id==importData.component_id,
                    analysis_result.c.project==importData.project,
                    # analysis_result.c.sample_source==importData.sample_source
                ))
                result = conn.execute(stmt).fetchall()
                if result:
                    raise HTTPException(status_code=500, detail=f"分析结果{importData.sample_name}已存在!")
            else:
                sample_id = ""
                

            

            analysis_result_id = str(uuid.uuid4())
            stmt = analysis_result.insert().values(
                component_id=importData.component_id,
                project=importData.project,
                # analysis_method=analysis_method,
                content=importData.content,
                # sample_id=sample_id,
                analysis_result_id=analysis_result_id,
                file_name=importData.file_name,
                # sample_source=importData.sample_source,
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

@sample_result.post("/analysis-result/update-analsyis-result/{analysis_result_id}",tags=['analsyis_result'])
async def update_analsyis_result(analysis_result_id, updateAnalysisResult:UpdateAnalysisResult):
    with get_engine().begin() as conn:
        stmt = analysis_result.update() 
        stmt = stmt.where(analysis_result.c.analysis_result_id == analysis_result_id)
        stmt = stmt.values(updateAnalysisResult.model_dump())
        conn.execute(stmt)
        conn.commit()
    return {"message":"success"}

@sample_result.get("/analysis-result/find-by-id/{analysis_result_id}",tags=['analsyis_result'])
async def find_by_id(analysis_result_id):
    with get_engine().begin() as conn:
        result = analysis_result_service.find_by_analysis_result_id(conn,analysis_result_id)
    return result




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

def get_unique_filename(upload_dir: str, filename: str) -> str:
    """
    如果文件已存在，则自动在文件名后加 (1)、(2)... 直到唯一
    """
    name, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename

    while os.path.exists(os.path.join(upload_dir, new_filename)):
        new_filename = f"{name}({counter}){ext}"
        counter += 1

    return new_filename


@sample_result.post("/analysis-result/upload",tags=['analysis_result'])
async def upload(
    component_id: str = Form(...),
    project: str = Form(...),
    file: UploadFile = File(...)):
    with get_engine().begin() as conn:
        component = pipeline_service.find_component_by_id(conn,component_id)
    file_type = component.get("file_type","collected")
    settings = get_settings()
    UPLOAD_DIR =  f"{settings.DATA_DIR}/{project}"
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    unique_name  = get_unique_filename(UPLOAD_DIR, file.filename)
    file_path = os.path.join(UPLOAD_DIR,unique_name)


     # 检查文件类型
    allowed_exts = [".xlsx", ".xls", ".csv", ".tsv"]
    name, ext = os.path.splitext(file.filename)
    ext = ext.lower()

    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {ext}")


    if ext == ".tsv":
        # 直接保存 TSV 文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(">>>> TSV 文件已保存:", file_path)
        # return {
        #     "file_path": file_path,
        # }
    else:
        temp_path = os.path.join(UPLOAD_DIR, f"temp_{unique_name}")
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(">>>> 原始文件已保存:", temp_path)

        # 转换为 TSV 格式
        tsv_filename = os.path.splitext(unique_name)[0] + ".tsv"
        file_path = os.path.join(UPLOAD_DIR, tsv_filename)

        try:
            if ext in [".xlsx", ".xls"]:
                df = pd.read_excel(temp_path)
            elif ext == ".csv":
                df = pd.read_csv(temp_path)
   

            df.to_csv(file_path, sep="\t", index=False)
            print(f">>>> 已转换为 TSV: {file_path}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"文件转换失败: {str(e)}")
        # finally:
        #     # 可选：删除原始文件，只保留 TSV
        #     if ext != ".tsv" and os.path.exists(temp_path):
        #         os.remove(temp_path)

    # with open(file_path, "wb") as buffer:
    #     shutil.copyfileobj(file.file, buffer)
    #     print(">>>>file saved to ",file_path)
    import_data_list =[
        ImportData(
            component_id= component_id,
            project= project,
            content= file_path,
            file_type= file_type,
            file_name= unique_name,
            # sample_source= "source",
        )
    ]
    await import_data(import_data_list)
    # component_id:str
    # project: str
    # content: str
    # sample_name: Optional[str]=None
    # file_type: str
    # sample_source: str
    # file_name: Optional[str]=None

    return {
        "file_path": file_path,
    }

@sample_result.get("/analysis-result/download-example/{component_id}",tags=['analysis_result'])
async def download_example(component_id):
    with get_engine().begin() as conn:
        example_file,example_url,component = pipeline_service.get_example(conn,component_id)
    return {
        "example_file": example_file,
        "example_url": example_url
    }

@sample_result.post("/analysis-result/add-example/{component_id}",tags=['analysis_result'])
async def download_example(component_id,project):
    with get_engine().begin() as conn:
        example_file,example_url,component = pipeline_service.get_example(conn,component_id)

    import_data_list =[
        ImportData(
            component_id= component_id,
            project= project,
            content= example_file,
            file_type= component.file_type,
            file_name= "example",
            # sample_source= "source",
        )
    ]
    await import_data(import_data_list)
    return {
        "example_file": example_file,
        "example_url": example_url
    }

@sample_result.post("/analysis-result/create-metadata",tags=['analysis_result'])
async def create_metadata(project_id,component_id):
    with get_engine().begin() as conn:
        stmt = select(analysis_result).where(and_(
            analysis_result.c.project==project_id,
            analysis_result.c.component_id==component_id
        ))
        result = conn.execute(stmt).mappings().all()
        for item in result:
            if item["sample_id"]:
                stmt = select(samples).where(samples.c.sample_id==item["sample_id"])
                sample = conn.execute(stmt).mappings().first()
                if not sample:
                    # 如果样本不存在，则创建样本
                    stmt = insert(samples).values(
                        sample_id=item["sample_id"],
                        project=project_id,
                        sample_name=item["file_name"]
                    )
                    conn.execute(stmt)
            else:
                str_id = str(uuid.uuid4())

                # create sample
                stmt = insert(samples).values(
                        sample_id=str_id,
                        project=project_id,
                        sample_name=item["file_name"]
                    )
                conn.execute(stmt)
                # update analysis_result sample_id
                stmt = analysis_result.update().values(sample_id=str_id).where(analysis_result.c.analysis_result_id==item["analysis_result_id"])
                conn.execute(stmt)
    
@sample_result.post("/analysis-result/batch-bind-sample/{component_id}",tags=['analysis_result'])
async def batch_bind_sample(component_id, project_id):
    with get_engine().begin() as conn:
        stmt = select(analysis_result).where(and_(
            analysis_result.c.component_id==component_id,
            analysis_result.c.project==project_id,
        ))
        result = conn.execute(stmt).mappings().all()
        stmt = select(samples).where(samples.c.project==project_id)
        sample = conn.execute(stmt).mappings().all()

        sample_dict = {item['sample_name']:item['sample_id'] for item in sample}
        for item in result:
            if item["file_name"] in sample_dict:
                sample_id = sample_dict[item["file_name"]]
                # update analysis_result sample_id
                stmt = analysis_result.update().values(sample_id=sample_id).where(analysis_result.c.analysis_result_id==item["analysis_result_id"])
                conn.execute(stmt)
    return {"message":"success"}
        




@sample_result.post("/analysis-result/batch-remove/{component_id}",tags=['analysis_result'])
async def batch_remove(component_id, project_id):
    with get_engine().begin() as conn:
        stmt = analysis_result.delete().where(and_(
            analysis_result.c.component_id==component_id,
            analysis_result.c.project==project_id,
        ))
        conn.execute(stmt)
    return {"message":"success"}