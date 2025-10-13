from fastapi import APIRouter,Depends,Request,HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from brave.api.enum.component_script import ScriptName
from brave.api.service.pipeline  import find_module
# from brave.api.config.db import conn
# from models.user import users
from typing import List
from starlette.status import HTTP_204_NO_CONTENT
from sqlalchemy import func, select
from brave.api.models.orm import SampleAnalysisResult
import glob
import importlib
import os
from brave.api.config.db import get_db_session
from sqlalchemy import and_,or_
from io import BytesIO
import base64
import json
import traceback
import uuid
import pandas as pd
from brave.api.config.db import get_engine
from brave.api.models.core import samples
import inspect
import  brave.api.service.pipeline as pipeline_service

# from brave.api.routes.analysis import get_db_value
from brave.api.utils.get_db_utils import get_ids
file_parse_plot = APIRouter()
from brave.api.config.config import get_settings
from pathlib import Path
from brave.api.service.analysis_result_service import find_analyais_result_by_ids

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

     
def get_db_dict(conn,db_field,request_param):
    db_ids_dict = {key: get_ids(request_param[key]) for key in db_field if key in request_param}
    # with get_db_session() as session:
    # get_db_value
    db_dict = { key:find_analyais_result_by_ids(conn,value) for key,value in  db_ids_dict.items()}
    return db_dict

# 实现模块默认隔离，通过module_dir实现模块共享
# 指定了module_dir，从module_dir所在目录查找模块
# pipeline/share/py_plot/abundance_difference.py
# 未指定module_dir，从pipeline_key所在目录查找模块
# pipeline/reads-alignment-based-abundance-analysis/py_plot/abundance_alpha_diversity.py
def parse_result(request_param,module_name):
    module_dir = request_param['component_id']
    with get_engine().begin() as conn:
        component = pipeline_service.find_pipeline_by_id(conn, module_dir)
        if not component:
            raise HTTPException(status_code=500, detail=f"根据{module_dir}不能找到记录!")

        # if "module_dir" in request_param:
        #     module_dir = request_param['module_dir']
        py_module = {}# find_module(component.namespace,module_dir,ScriptName.output_parse,'py')['module']
        # if module_dir not in all_module:
        #     raise HTTPException(status_code=500, detail=f"py_plot: 目录{module_dir}没有找到!")
        # py_module_dir = all_module[module_dir]
        # if module_name not in py_module_dir:
        #     raise HTTPException(status_code=500, detail=f"py_plot: 目录{module_dir}文件{module_name}没有找到!")
        # py_module = py_module_dir[module_name]['module']
        module = importlib.import_module(py_module)
        parse_data = getattr(module, "parse_data")
        sig = inspect.signature(parse_data)
        params = sig.parameters.keys()
        args = {
            "request_param":request_param,
        }
        if hasattr(module, "get_db_field"):
            get_db_field = getattr(module, "get_db_field")
            db_field = get_db_field()
            db_dict = get_db_dict(conn,db_field,request_param)
            if "db_dict" in params:
                args.update({"db_dict":db_dict})
            else:
                args.update(db_dict)
        
        if "sample" in params:
            sample = get_sample(request_param['project'])
            args.update({"sample":sample})
        
    # data = None
    # if len(params) ==1:
    #     data = parse_data(request_param)
    # elif len(params) ==2:
    #     if hasattr(module, "get_db_field"):
    #         get_db_field = getattr(module, "get_db_field")
    #         db_field = get_db_field()
    #         db_dict = get_db_dict(db_field,request_param)
    #         data = parse_data(request_param,db_dict)
    #     else:
    #         sample = get_sample(request_param['project'])
    #         data = parse_data(request_param,sample)
    # else:
    #     get_db_field = getattr(module, "get_db_field")
    #     db_field = get_db_field()
    #     db_dict = get_db_dict(db_field,request_param)
    #     sample = get_sample(request_param['project'])
    #     data = parse_data(request_param,db_dict,sample)

    data = parse_data(**args)
    result = {}
    # if isinstance(data,list):

    if isinstance(data,dict):
        new_data = []
        for key, value in data.items():
            if not key.startswith("in_"):
                value = format_output(value,request_param)
                new_data.append(value)
        result= {"dataList":new_data}
    elif isinstance(data,tuple):
        new_data = []
        for item in data:
            if not isinstance(item,tuple) and not isinstance(item,list):
                if item is not None:
                    item = format_output(item,request_param)
                    new_data.append(item)
                # if isinstance(item, pd.DataFrame):
                #     new_data.append(item.to_dict(orient="records"))
                # else:
                #     if item:
                #         new_data.append(item)
        
        result = {"dataList":new_data}
    elif isinstance(data,list):
        pass
    else:
        new_data = format_output(data,request_param)
        result = {"dataList":[new_data]}
        # if isinstance(data, pd.DataFrame):
        #     # result = {"data":data.to_dict(orient="records")}
        #     result = {"data":json.loads(data.to_json(orient="records"))}
        # else:
        #     result = {"data":data}  
             
    if hasattr(module, "parse_plot"):
        parse_plot = getattr(module, "parse_plot")
        try:
            plt = parse_plot(data, request_param)
            if isinstance(plt,dict):
                for key, value in plt.items():
                    # buf = BytesIO()
                    # value.savefig(buf, format='png', bbox_inches='tight')
                    # value.close()  # 关闭图像以释放内存
                    # buf.seek(0)
                    # img_base64 = base64.b64encode(buf.read()).decode('utf-8')
                    img = format_img_output(value,request_param)
                    result.update({key:img })
            elif isinstance(plt,list):
                img_list = []
                for value in plt:
                    img = format_img_output(value,request_param)
                    img_list.append(img)
                result.update({"img": img_list})
                
            else:
                # buf = BytesIO()
                # plt.savefig(buf, format='png', bbox_inches='tight')
                # plt.close()  # 关闭图像以释放内存
                # buf.seek(0)
                # img_base64 = base64.b64encode(buf.read()).decode('utf-8')
                img = format_img_output(plt,request_param)
                result.update({"img":img})
        except Exception as e:
            # print("发生异常：",e.with_traceback())
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=json.dumps(e.args))
    
    return result


def get_downstream_analysis_result_dir(request_param,suffix):
    settings = get_settings()
    base_dir = settings.BASE_DIR
    project,analysis_method = request_param['project'],request_param['analysis_method']
    
    downstream_analysis_result_dir  =   base_dir / project / "downstream_analysis_result" /analysis_method 
    if not downstream_analysis_result_dir.exists():
        downstream_analysis_result_dir.mkdir(parents=True,  exist_ok=True)
    str_uuid = str(uuid.uuid4())
    downstream_analysis_result = downstream_analysis_result_dir / f"{str_uuid}.{suffix}"
    file_name = str(downstream_analysis_result).replace(str(base_dir),"")
    return downstream_analysis_result,file_name


def format_img_output(plt,request_param):
    imgType = request_param['imgType']
    downstream_analysis_result,file_name = get_downstream_analysis_result_dir(request_param,imgType)
    plt.savefig(downstream_analysis_result, format='pdf', bbox_inches='tight')

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()  # 关闭图像以释放内存
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    img_base64 = "data:image/png;base64," + img_base64
    return {
        "data":img_base64,
        "type":"img",
        "url":f"/brave-api/dir{file_name}"
    }

# 如果请求中没有analysis_method 则不保存
def format_output(item,request_param):
    setting = get_settings()
    base_dir = str(setting.BASE_DIR)
    work_dir = str(setting.WORK_DIR)
    if  isinstance(item, pd.DataFrame):
        file_name = ""
        if "origin"   in request_param and "file_path" in request_param  :
            file_path = request_param['file_path']
            if os.path.islink(file_path):
                link_path = Path(file_path)
                real_path = link_path.resolve()
                file_name = str(real_path).replace(work_dir,"/brave-api/work-dir")
            else:
                file_name = file_path.replace(base_dir,"/brave-api/dir")
        else:     
            table_type = request_param['table_type']
            downstream_analysis_result,file_name = get_downstream_analysis_result_dir(request_param,table_type)
            file_name = f"/brave-api/dir{file_name}"
            if table_type=='tsv':
                item.to_csv(downstream_analysis_result, sep="\t", index=False)
            elif table_type=='xlsx':
                item.to_excel(downstream_analysis_result,  index=False)
        

        return  {
            "data":json.loads(item.to_json(orient="records")) ,
            "type":"table",
            "url":f"{file_name}"
        }
    elif isinstance(item, str):
        if item == 'html':
            file_path = request_param['file_path']
            file_name = file_path.replace(base_dir,"/brave/brave-api/dir")
            return {
                "data":file_name,
                "type":"html",
                "url":f"/brave-api/dir{file_name}"
            }
        return {
            "data":item,
            "type":"string",
        }
    else:
        return item


@file_parse_plot.get("/fast-api/file-parse-plot-test")
async def parse_result_restful():
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
    is_save_analysis_result = request_param['is_save_analysis_result']
    result = parse_result(request_param,module_name)
    if is_save_analysis_result:
        save_plot_result(result,request_param)
    return result

def save_plot_result(result, request_param):
    file_path = None
    if "id" in request_param:
        with get_db_session() as db:
            sampleAnalysisResult = db.query(SampleAnalysisResult) \
                .filter(SampleAnalysisResult.id == request_param["id"]).first()
        file_path =   sampleAnalysisResult.content
    else:
        file_path ,file_name= get_downstream_analysis_result_dir(request_param,"json")
        # str_uuid = str(uuid.uuid4())
        # file_path = f"/ssd1/wy/workspace2/nextflow-fastapi/analysis_result/{str_uuid}.json"

    
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
        "analysis_name":analysis_name,
        "analysis_type":"script"
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
    

@file_parse_plot.post("/fast-api/file-save-parse-plot/{module_name}")
async def parse_result_restful(module_name,request_param: Dict[str, Any]):
    # base_path ="/ssd1/wy/workspace2/test/test_workspace/result/V1.0"
    # verison = "V1.0"
    # project="test"
    # file_path ="/ssd1/wy/workspace2/leipu/leipu_workspace2/output/prokka/OSP-3/OSP-3.txt"
    # module_name = "prokka_txt_plot"
    # data = await request.json()

    result = parse_result(request_param,module_name)
    save_plot_result(result)
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