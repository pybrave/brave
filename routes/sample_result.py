from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session

from config.db import conn
# from models.user import users
from typing import List
from starlette.status import HTTP_204_NO_CONTENT
from sqlalchemy import func, select
from config.db import SessionLocal
from cryptography.fernet import Fernet
from models.orm import SampleAnalysisResult,Sample
import glob
import importlib
import os
import json
from config.db import get_db_session
from sqlalchemy import and_,or_
from schemas.analysis_result import AnalysisResultQuery,AnalysisResult
from models.core import samples,analysis_result
from config.db import engine
sample_result = APIRouter()
# key = Fernet.generate_key()
# f = Fernet(key)


# def get_all_subclasses(cls):
#     subclasses = set(cls.__subclasses__())
#     for subclass in subclasses.copy():
#         subclasses.update(get_all_subclasses(subclass))
#     return subclasses


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

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
    py_files = [f for f in os.listdir("sample_result_parse") if f.endswith('.py')]
    for py_file in py_files:
        module_name = py_file[:-3]  # 去掉 `.py` 后缀，获取模块名
        module = importlib.import_module(f'sample_result_parse.{module_name}')
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
def parse_result_restful():
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
def parse_result_restful():
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
def parse_result_restful():
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
def parse_result_restful(base_path,verison,project):
    # base_path ="/ssd1/wy/workspace2/test/test_workspace/result"
    # verison = "V1.0"
    
    dir_list = glob.glob(f"{base_path}/{verison}/*",recursive=True)
    for dir_path in dir_list:
        parse_result(dir_path,project,verison)
    return {"msg":"success"}


@sample_result.post(
    "/fast-api/find-analyais-result-by-analysis-method",
    response_model=List[AnalysisResult])
def find_analyais_result_by_analysis_method(analysisResultQuery:AnalysisResultQuery):
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
    with engine.begin() as conn:
        stmt = analysis_result.select() 
        if analysisResultQuery.querySample:
            stmt =  select(analysis_result, samples).select_from(analysis_result.outerjoin(samples,samples.c.sample_key==analysis_result.c.sample_key))
        stmt= stmt.where(and_(analysis_result.c.analysis_method.in_(analysisResultQuery.analysis_method) \
            ,analysis_result.c.project ==analysisResultQuery.project \
            ))
        result  = conn.execute(stmt)
        # result = result.fetchall()
        rows = result.mappings().all()
        result_dict = [AnalysisResult(**row) for row in rows]
        # result_dict = []
        for item in result_dict:
            if item.content_type=="json":
                item.content = json.loads(item.content)
        #     result.append(row)
        # # rows = result.mappings().all()
        # pass
    return result_dict
    # return {"aa":"aa"}

@sample_result.post(
    "/fast-api/add-sample-analysis",
    tags=['analsyis_result'],
    description="根据项目名称导入样本")
def add_sample_analysis(project):
    insert_sample_list = []
    with engine.begin() as conn:
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



# @user.get(
#     "/users",
#     tags=["users"],
#     response_model=List[User],
#     description="Get a list of all users",
# )
# def get_users():
#     return conn.execute(users.select()).fetchall()


    

# @user.get("/users/count", tags=["users"], response_model=UserCount)
# def get_users_count():
#     result = conn.execute(select([func.count()]).select_from(users))
#     return {"total": tuple(result)[0][0]}


# @user.get(
#     "/users/{id}",
#     tags=["users"],
#     response_model=User,
#     description="Get a single user by Id",
# )
# def get_user(id: str):
#     return conn.execute(users.select().where(users.c.id == id)).first()


# @user.post("/", tags=["users"], response_model=User, description="Create a new user")
# def create_user(user: User):
#     new_user = {"name": user.name, "email": user.email}
#     new_user["password"] = f.encrypt(user.password.encode("utf-8"))
#     result = conn.execute(users.insert().values(new_user))
#     return conn.execute(users.select().where(users.c.id == result.lastrowid)).first()


# @user.put(
#     "users/{id}", tags=["users"], response_model=User, description="Update a User by Id"
# )
# def update_user(user: User, id: int):
#     conn.execute(
#         users.update()
#         .values(name=user.name, email=user.email, password=user.password)
#         .where(users.c.id == id)
#     )
#     return conn.execute(users.select().where(users.c.id == id)).first()


# @user.delete("/{id}", tags=["users"], status_code=HTTP_204_NO_CONTENT)
# def delete_user(id: int):
#     conn.execute(users.delete().where(users.c.id == id))
#     return conn.execute(users.select().where(users.c.id == id)).first()