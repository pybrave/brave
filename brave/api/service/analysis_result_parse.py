from ast import Dict, Set
import asyncio
import psutil
from watchfiles import awatch
from datetime import datetime
from brave.api.config.db import get_engine
from brave.api.models.core import analysis
from sqlalchemy import select, update
import logging
from importlib.resources import files
from importlib import import_module
import inspect
from brave.api.service.sse_service import SSESessionService
from collections import defaultdict
from typing import Dict, Set,Any
import brave.api.service.analysis_service as analysis_service
import brave.api.service.analysis_result_service as analysis_result_service
# 创建 logger
logger = logging.getLogger(__name__)

class AnalysisResultParse:
    def __init__(self, sse_service: SSESessionService,check_interval: int = 5  ):
        self.queue_process = asyncio.Queue()
        self.queue_lock = asyncio.Lock()  # 保证数据库更新和队列操作安全
        self.check_interval = check_interval  # 检查间隔
        # self.listener_files = self._load_listener_files()
        self.sse_service = sse_service
        self.analysis_id_to_sample: Dict[str, Any] ={}
        self.analysis_id_to_params: Dict[str, Any] = {}
        self.analysis_id_to_map_filename_sample_id: Dict[str, Any] = {}
        self._load_parsed_analysis_result()

    def _load_parsed_analysis_result(self):
        """
        加载已经解析过的分析结果
        """
        with get_engine().begin() as conn:
            analysis_list = analysis_service.find_running_analysis(conn)
            analysis_id_list = [item['analysis_id'] for item in analysis_list]
            for analysis_id in analysis_id_list:
                self.add_sample(conn,analysis_id)
                self.add_params(conn,analysis_id)
            
    
    def add_sample(self,conn,analysis_id):
        analysis_result_list = analysis_result_service.find_analysis_result_by_analysis_id(conn,analysis_id)
        sample_id_list = [item['sample_id'] for item in analysis_result_list]
        self.analysis_id_to_sample[analysis_id] = sample_id_list

    def add_params(self,conn,analysis_id):
        params:Any = self.load_parse_params(conn,analysis_id)
        self.analysis_id_to_params[analysis_id] = params

    def load_parse_params(self,conn,analysis_id):
        params:Any = analysis_service.get_parse_analysis_result_params(conn,analysis_id)
        # if "error" in params:
        #     return None
        return params

    def parse_analysis_result(self,analysis_id):
        params:Any = self.analysis_id_to_params[analysis_id]
        analysis:Any = params["analysis"]
        file_format_list = params["file_format_list"]
        parse = params["parse"]
        result_list,result_dict = analysis_service.execute_parse(analysis,parse,file_format_list)
        sample_list = self.analysis_id_to_map_filename_sample_id[analysis_id] 
        sample_dict = {item['sample_name']:item for item in sample_list}
        add_sample_list = []
        for item in result_list:
                if item['file_name'] in sample_dict:
                    item['sample_id'] = sample_dict[item['file_name']]['sample_id']
                    add_sample_list.append(item)
                # else:
                #     raise HTTPException(status_code=500, detail=f"样本{item['file_name']}不存在!")
        
        return result_list,result_dict

    

async def parse_analysis_result(analysis_id,save:Optional[bool]=False):
    with get_engine().begin() as conn:
        stmt = select(analysis).where(analysis.c.analysis_id == analysis_id)
        result = conn.execute(stmt).mappings().first()
        if not result:
            raise HTTPException(status_code=404, detail=f"Analysis with id {analysis_id} not found")
        component_id = result['component_id']
        component_ = pipeline_service.find_pipeline_by_id(conn, component_id)
        if not component_:
            raise HTTPException(status_code=404, detail=f"Component with id {component_id} not found")
        try:
            component_content = json.loads(component_.content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to parse component content: {e}")
        parse_analysis_result_module = component_content.get('parseAnalysisResultModule')
        
        component_file_list = pipeline_service.find_component_by_parent_id(conn,component_id,"software_output_file")
        if len(component_file_list) == 0:
            return {"error":"组件没有添加输出文件,请检查!"}
            # raise HTTPException(status_code=500, detail=f"组件{component_id}没有添加输出文件,请检查!")
        component_file_content_list = [{**json.loads(item.content),"component_id":item['component_id']} for item in component_file_list]
        file_format_list = [
            {"dir":item['dir'],"fileFormat":item['fileFormat'],"name":item['name'],"component_id":item['component_id']}
            for item in component_file_content_list if 'fileFormat' in item
        ]
        if not file_format_list:
            return {"error":"组件的输出文件没有配置fileFormat!请检查!"}
            # raise HTTPException(status_code=500, detail=f"组件{component_id}的输出文件没有配置fileFormat!请检查!")


        py_module = find_module(component_.namespace,"py_parse_analysis_result",component_id,parse_analysis_result_module,'py')['module']
        module = importlib.import_module(py_module)
        parse = getattr(module, "parse")


        result_dict = {}
        file_dict={}
        result_list = []
        for item in file_format_list:

            
            # module_dir = component_.pipeline_key
            # if "moduleDir" in pipeline_content:
            #     module_dir = pipeline_content['moduleDir']
            # 递归获取dir_path的文件
        
        
            dir_path = f"{result['output_dir']}/output/{item['dir']}"
            get_all_files_recursive(dir_path,item['dir'],file_dict)


            # if item['module'] not in all_module:
            #     raise HTTPException(status_code=500, detail=f"py_parse_analysis_result: {module_name}没有找到!")
            # py_module = all_module[]
            
            # # parse_result_one()
            moduleArgs = {}
            # if "moduleArgs" in item:
            #     moduleArgs = item['moduleArgs']
            
            
            res = None    
            args = {
                "dir_path":dir_path,
                # "analysis": dict(result),
                "file_format":item['fileFormat']
                # "args":moduleArgs,
            
            }
            res = parse(**args)
            
            for sub_item in  res:
                sub_item.update({
                    "component_id":item['component_id'],
                    # "analysis_name":item['name'],
                    # "analysis_method":item['name'],
                    "project":result['project'],
                    "analysis_id":analysis_id,
                    "analysis_type":"upstream_analysis"
                    })
            result_dict.update({item['name']:res})
            result_list = result_list + res
            
        if save:
            sample_name_list = [item['file_name'] for item in result_list]
            sample_list = sample_service.find_by_sample_name_list(conn,sample_name_list)
            sample_dict = {item['sample_name']:item for item in sample_list}
            for item in result_list:
                if item['file_name'] in sample_dict:
                    item['sample_id'] = sample_dict[item['file_name']]['sample_id']
                else:
                    raise HTTPException(status_code=500, detail=f"样本{item['file_name']}不存在!")
            analysis_result_service.save_or_update_analysis_result_list( conn,result_list)
            # parse_result_oneV2(res,item['name'],result['project'],"V1.0",analysis_id)
    return {"result_dict":result_dict,"file_format_list":file_format_list,"file_dict":file_dict}

