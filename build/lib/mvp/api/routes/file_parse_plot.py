from fastapi import APIRouter,Depends,Request,HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

# from mvp.api.config.db import conn
# from models.user import users
from typing import List
from starlette.status import HTTP_204_NO_CONTENT
from sqlalchemy import func, select
from cryptography.fernet import Fernet
from mvp.api.models.orm import SampleAnalysisResult
import glob
import importlib
import os
from mvp.api.config.db import get_db_session
from sqlalchemy import and_,or_
from io import BytesIO
import base64
import json
import traceback
import uuid
import pandas as pd
from mvp.api.config.db import get_engine
from mvp.api.models.core import samples
import inspect
from mvp.api.routes.analysis import get_db_value
from mvp.api.utils.get_db_utils import get_ids
file_parse_plot = APIRouter()
# key = Fernet.generate_key()
# f = Fernet(key)


def get_all_subclasses(cls):
    subclasses = set(cls.__subclasses__())
    for subclass in subclasses.copy():
        subclasses.update(get_all_subclasses(subclass))
    return subclasses



def get_sample(project):
    with get_engine().begin() as conn:
        result =  conn.execute(samples.select() \
            .where(samples.c.project==project)) 
              
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df

     
def get_db_dict(db_field,request_param):
    db_ids_dict = {key: get_ids(request_param[key]) for key in db_field if key in request_param}
    with get_db_session() as session:
        db_dict = { key:get_db_value(session,value) for key,value in  db_ids_dict.items()}
    return db_dict

def parse_result(request_param,module_name):
    module = importlib.import_module(f'mvp.api.file_parse_plot.{module_name}')
    parse_data = getattr(module, "parse_data")
    sig = inspect.signature(parse_data)
    params = sig.parameters
    data = None
    if len(params) ==1:
        data = parse_data(request_param)
    elif len(params) ==2:
        if hasattr(module, "get_db_field"):
            get_db_field = getattr(module, "get_db_field")
            db_field = get_db_field()
            db_dict = get_db_dict(db_field,request_param)
            data = parse_data(request_param,db_dict)
        else:
            sample = get_sample(request_param['project'])
            data = parse_data(request_param,sample)
    else:
        get_db_field = getattr(module, "get_db_field")
        db_field = get_db_field()
        db_dict = get_db_dict(db_field,request_param)
        sample = get_sample(request_param['project'])
        data = parse_data(request_param,db_dict,sample)


    result = {}
    # if isinstance(data,list):

    if isinstance(data,dict):
        new_data = {}
        for key, value in data.items():
            if key.startswith("in_"):
                pass
            elif isinstance(value, pd.DataFrame):
                new_data[key] = value.to_dict(orient="records")
            else:
                new_data[key] = value
        result= new_data
    elif isinstance(data,tuple):
        new_data = []
        for item in data:
            if not isinstance(item,tuple):
                if isinstance(item, pd.DataFrame):
                    new_data.append(item.to_dict(orient="records"))
                else:
                    new_data.append(item)
        result = {"dataList":new_data}
    else:
        if isinstance(data, pd.DataFrame):
            # result = {"data":data.to_dict(orient="records")}
            result = {"data":json.loads(data.to_json(orient="records"))}
            
        else:
            result = {"data":data}  
             
    if hasattr(module, "parse_plot"):
        parse_plot = getattr(module, "parse_plot")
        try:
            plt = parse_plot(data, request_param)
            if isinstance(plt,dict):
                for key, value in plt.items():
                    buf = BytesIO()
                    value.savefig(buf, format='png', bbox_inches='tight')
                    value.close()  # 关闭图像以释放内存
                    buf.seek(0)
                    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
                    result.update({key:"data:image/png;base64," + img_base64 })
            elif isinstance(plt,list):
                img_list = []
                for value in plt:
                    buf = BytesIO()
                    value.savefig(buf, format='png', bbox_inches='tight')
                    value.close()  # 关闭图像以释放内存
                    buf.seek(0)
                    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
                    img_list.append("data:image/png;base64," + img_base64)
                result.update({"img": img_list})
                
            else:
                buf = BytesIO()
                plt.savefig(buf, format='png', bbox_inches='tight')
                plt.close()  # 关闭图像以释放内存
                buf.seek(0)
                img_base64 = base64.b64encode(buf.read()).decode('utf-8')
                result.update({"img":"data:image/png;base64," + img_base64 })
        except Exception as e:
            # print("发生异常：",e.with_traceback())
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=json.dumps(e.args))
    
    return result

@file_parse_plot.get("/fast-api/file-parse-plot-test")
def parse_result_restful():
    # base_path ="/ssd1/wy/workspace2/test/test_workspace/result/V1.0"
    # verison = "V1.0"
    # project="test"
    file_path ="/ssd1/wy/workspace2/leipu/leipu_workspace2/output/prokka/OSP-3/OSP-3.txt"
    module_name = "prokka_txt_plot"
    result = parse_result(file_path, module_name)
    return result
# @file_parse_plot.post("/fast-api/file-parse-plot")
# async def parse_result_restful(request: Request):
#     # base_path ="/ssd1/wy/workspace2/test/test_workspace/result/V1.0"
#     # verison = "V1.0"
#     # project="test"
#     # file_path ="/ssd1/wy/workspace2/leipu/leipu_workspace2/output/prokka/OSP-3/OSP-3.txt"
#     # module_name = "prokka_txt_plot"
#     data = await request.json()
#     # result = parse_result(file_path, module_name)
#     return result

@file_parse_plot.post("/fast-api/file-parse-plot/{module_name}")
async def parse_result_restful(module_name,request_param: Dict[str, Any]):
    # base_path ="/ssd1/wy/workspace2/test/test_workspace/result/V1.0"
    # verison = "V1.0"
    # project="test"
    # file_path ="/ssd1/wy/workspace2/leipu/leipu_workspace2/output/prokka/OSP-3/OSP-3.txt"
    # module_name = "prokka_txt_plot"
    # data = await request.json()
    result = parse_result(request_param,module_name)
    return result

@file_parse_plot.post("/fast-api/file-save-parse-plot/{module_name}")
async def parse_result_restful(module_name,request_param: Dict[str, Any]):
    # base_path ="/ssd1/wy/workspace2/test/test_workspace/result/V1.0"
    # verison = "V1.0"
    # project="test"
    # file_path ="/ssd1/wy/workspace2/leipu/leipu_workspace2/output/prokka/OSP-3/OSP-3.txt"
    # module_name = "prokka_txt_plot"
    # data = await request.json()
    file_path = None
    if "id" in request_param:
        with get_db_session() as db:
            sampleAnalysisResult = db.query(SampleAnalysisResult) \
                .filter(SampleAnalysisResult.id == request_param["id"]).first()
        file_path =   sampleAnalysisResult.content
    else:
        str_uuid = str(uuid.uuid4())
        file_path = f"/ssd1/wy/workspace2/nextflow-fastapi/analysis_result/{str_uuid}.json"

    result = parse_result(request_param,module_name)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    software = request_param['software']
    project = request_param['project']
    analysis_method = request_param['analysis_method']
    analysis_name = request_param['analysis_name']
    new_analysis = {
        "request_param":json.dumps(request_param),
        "software":software ,
        "content_type":"file",
        "content":file_path,
        "project":project, 
        "analysis_method":analysis_method,
        "analysis_name":analysis_name
    }
    with get_db_session() as db:
        if "id" in request_param:
            db.query(SampleAnalysisResult) \
                .filter(SampleAnalysisResult.id == request_param["id"]) \
                    .update(new_analysis)
        else:
            analysisResult = SampleAnalysisResult(**new_analysis)
            db.add(analysisResult)
        db.commit()
        
    return result



# def update_or_save_result(request_param, software, content_type, content, db, project, verison, analysis_method,analysis_name):
#         # sampleAnalysisResult = db.query(SampleAnalysisResult) \
#         # .filter(and_(SampleAnalysisResult.analysis_method == analysis_method,\
#         #         SampleAnalysisResult.analysis_version == verison, \
#         #         SampleAnalysisResult.analysis_key == analysis_key, \
#         #         SampleAnalysisResult.project == project \
#         #     )).first()
#         # if sampleAnalysisResult:
#         #     sampleAnalysisResult.sample_name = sample_name
#         #     sampleAnalysisResult.content = content
#         #     sampleAnalysisResult.content_type = content_type
#         #     sampleAnalysisResult.analysis_name = analysis_name
#         #     # sampleAnalysisResult.log_path = log_path
#         #     sampleAnalysisResult.software = software
#         #     db.commit()
#         #     db.refresh(sampleAnalysisResult)
#         #     print(">>>>更新: ",sample_name, software, content_type)
#         # else:
#         sampleAnalysisResult = SampleAnalysisResult(analysis_method=analysis_method, \
#             analysis_version=verison, \
#             request_param=request_param, \
#             content_type=content_type, \
#             analysis_name=analysis_name, \
#             # log_path=log_path, \
#             software=software, \
#             project=project, \
#             content=content \
#                 )
#         db.add(sampleAnalysisResult)
#         db.commit()
#         print(">>>>新增: ",analysis_method, content_type)


@file_parse_plot.get("/fast-api/read-json")
async def read_json_restful(path):
    with open(path,"r") as f:
        res = json.load(f)
        return res