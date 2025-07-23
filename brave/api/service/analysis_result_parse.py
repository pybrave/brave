from ast import Dict, Set
import asyncio
import json
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
from typing import Dict, Set,Any,List
import brave.api.service.analysis_service as analysis_service
import brave.api.service.analysis_result_service as analysis_result_service
import brave.api.service.sample_service as sample_service
from functools import lru_cache
from fastapi import Depends
from brave.api.service.listener_files_service import get_listener_files_service
from brave.api.service.listener_files_service import ListenerFilesService
from brave.api.core.evenet_bus import EventBus
# 创建 logger
logger = logging.getLogger(__name__)

class AnalysisResultParse:
    def __init__(self):
        # self.queue_process = asyncio.Queue()
        self.queue_lock = asyncio.Lock()  # 保证数据库更新和队列操作安全
        # self.check_interval = check_interval  # 检查间隔
        # self.listener_files = self._load_listener_files()
        # self.sse_service = sse_service
        # self.listener_files_service = listener_files_service
        self.analysis_id_to_analysis_result: Dict[str, List[Any]] =defaultdict(list)
        self.analysis_id_to_params: Dict[str, Any] = defaultdict(dict)
        self.analysis_id_list: List[str] = []
        self.remove_analysis_id_list: List[str] = []
        self.change_analysis_id_list = asyncio.Queue()
        # self.lock = asyncio.Lock()
        self.analysis_locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

        # self._load_parsed_analysis_result()

    # def _load_parsed_analysis_result(self):
    #     """
    #     加载已经解析过的分析结果
    #     """
    #     with get_engine().begin() as conn:
    #         analysis_list = analysis_service.find_running_analysis(conn)
    #         analysis_id_list = [item['analysis_id'] for item in analysis_list]
    #         for analysis_id in analysis_id_list:
    #             self.add_sample(conn,analysis_id)
    #             self.add_params(conn,analysis_id)
    async def add_analysis_id(self,analysis_id):
        async with self.analysis_locks[analysis_id]:
            self.analysis_id_list.append(analysis_id)
    async def add_remove_analysis_id(self,analysis_id):
        async with self.analysis_locks[analysis_id]:
            self.remove_analysis_id_list.append(analysis_id)

    async def add_change_analysis_id(self,analysis_id):
        async with self.analysis_locks[analysis_id]:
            if analysis_id  in self.analysis_id_list:
                await self.change_analysis_id_list.put(analysis_id)

 

    def remove_analysis_id(self,analysis_id):
        if analysis_id in self.analysis_id_list:
            self.analysis_id_list.remove(analysis_id)
            # self.reomve_analysis_result(analysis_id)

    def reomve_analysis_result(self,analysis_id):
        if analysis_id in self.analysis_id_to_analysis_result:
            del self.analysis_id_to_analysis_result[analysis_id]
        if analysis_id in self.analysis_id_to_params:
            del self.analysis_id_to_params[analysis_id]

    
    def remove_analysis_result_by_analsyis_result_id(self,analysis_id,analysis_result_id):
        if analysis_id in self.analysis_id_to_analysis_result:
            analysis_result_list = self.analysis_id_to_analysis_result[analysis_id]
            analysis_result_list = [item for item in analysis_result_list if item['analysis_result_id'] != analysis_result_id]
            self.analysis_id_to_analysis_result[analysis_id] = analysis_result_list

    
    # def is_analysis_id_exist(self,analysis_id):
    #     return analysis_id in self.change_analysis_id_list


   
    def cached_analysis_result(self):
        return self.analysis_id_to_analysis_result
    def cached_params(self):
        return self.analysis_id_to_params



    def find_parse_params(self,conn,analysis_id,preview):
        if preview:
            return analysis_service.get_parse_analysis_result_params(conn,analysis_id)
        if analysis_id in self.analysis_id_to_params:
            return self.analysis_id_to_params[analysis_id]
        else:
            params:Any = analysis_service.get_parse_analysis_result_params(conn,analysis_id)
            self.analysis_id_to_params[analysis_id] = params
            return params

    def find_analysis_result_exist(self,conn,analysis_id,component_id,sample_id,project,preview):
        if preview:
            return analysis_result_service.find_analysis_result_exist(conn,component_id,sample_id,project)
        if analysis_id in self.analysis_id_to_analysis_result:
            analysis_result_list = self.analysis_id_to_analysis_result[analysis_id]
            item = next((item for item in analysis_result_list if item['component_id'] == component_id and item['sample_id'] == sample_id and item['project'] == project), None)
            if item:
                return item
            else:
                result = analysis_result_service.find_analysis_result_exist(conn,component_id,sample_id,project)
                if result:
                    self.analysis_id_to_analysis_result[analysis_id].append(result)
                return result
        else:
            result = analysis_result_service.find_analysis_result_exist(conn,component_id,sample_id,project)
            if result:
                self.analysis_id_to_analysis_result[analysis_id].append(result)
            return result
            
    def find_by_sample_name_and_project(self,conn,sample_name,project):
        result = sample_service.find_by_sample_name_and_project(conn,sample_name,project)
        return result
    def find_file_dict(self,file_format_list,output_dir):
        file_dict = analysis_service.get_file_dict(file_format_list,output_dir)
        return file_dict


    async def auto_save_analysis_result(self):
        while True:
            try:
                analysis_id = await asyncio.wait_for(self.change_analysis_id_list.get(), timeout=0.5)
                print(f"自动解析分析: {analysis_id} !")
                with get_engine().begin() as conn:
                    await self.save_analysis_result(conn,analysis_id,True)

            except asyncio.TimeoutError:
                if self.change_analysis_id_list.empty():
                    for analysis_id in self.remove_analysis_id_list:
                        await asyncio.sleep(0.05)
                        # print(f"删除分析: {analysis_id} !")
                        # self.remove_analysis_id(analysis_id)
                        # self.reomve_analysis_result(analysis_id)
                        # self.remove_analysis_id_list = []
           
            # async with self.lock:
            # if not self.is_analysis_id_exist(analysis_id):
            #     return
            
  
            
            

    
    async def save_analysis_result(self,conn,analysis_id,preview):
     
        params,result_list,result_dict = self.parse_analysis_result(conn,analysis_id,preview)
        print("result_list",json.dumps(result_list,indent=4))
        for item in result_list:    
            result = self.find_analysis_result_exist(conn,analysis_id,item['component_id'],item['file_name'],item['project'],preview)
            if not result:
                find_sample = self.find_by_sample_name_and_project(conn,item['file_name'],item['project'])
                if find_sample:
                    item['sample_id'] = find_sample['sample_id']
              
                
                analysis_result_service.add_analysis_result(conn,item)
                # await self.listener_files_service.execute_listener("analysis_result_add",{
                #     "analysis":params['analysis'],
                #     "analysis_result":item,
                #     "sse_service":self.sse_service
                # })
                # data = json.dumps({
                #     "msg":f"分析{analysis_id}，文件{item['file_name']}保存成功!",
                #     "component_id":item['component_id'],
                #     "msgType":"analysis_result"
                # })
                # msg = {"group": "default", "data": data}
                # await self.sse_service.push_message(msg)
            else:
                if item['analysis_result_hash']!= result['analysis_result_hash']:
                    analysis_result_service.update_analysis_result(conn,result.id,item)
                    # await self.listener_files_service.execute_listener("analysis_result_update",{
                    #     "analysis":params['analysis'],
                    #     "analysis_result":item,
                    #     "sse_service":self.sse_service
                    # })
                    # data = json.dumps({
                    #     "msg":f"分析{analysis_id}，文件{item['file_name']}更新成功!",
                    #     "msgType":"analysis_result"
                    # })
                    # msg = {"group": "default", "data": data}
                    # await self.sse_service.push_message(msg)
        return params,result_list,result_dict


    def parse_analysis_result(self,conn,analysis_id,preview):
        params:Any = self.find_parse_params(conn,analysis_id,preview)
   
        result_list,result_dict = analysis_service.execute_parse(**params)
        return params,result_list,result_dict

    async def save_analysis_result_preview(self,conn,analysis_id):
        params,result_list,result_dict = await self.save_analysis_result(conn,analysis_id,True)
        file_format_list = params["file_format_list"]
        file_dict = self.find_file_dict(file_format_list,params['analysis']['output_dir'])   
        return {"result_dict":result_dict,"file_format_list":file_format_list,"file_dict":file_dict}

        
    async def parse_analysis_result_preview(self,conn,analysis_id):
        params,result_list,result_dict = self.parse_analysis_result(conn,analysis_id,True)
        file_format_list = params["file_format_list"]
        file_dict = self.find_file_dict(file_format_list,params['analysis']['output_dir'])   
        return {"result_dict":result_dict,"file_format_list":file_format_list,"file_dict":file_dict}
   

# @lru_cache()
# @inject
# def get_analysis_result_parse_service(
#     sse_service:SSESessionService=Provide[AppContainer.sse_service],
#     listener_files_service:ListenerFilesService=Depends(get_listener_files_service)
# ):
#     analysis_result_parse_service = AnalysisResultParse(sse_service,listener_files_service)
#     return analysis_result_parse_service


# async def parse_analysis_result(analysis_id,save:Optional[bool]=False):
#     with get_engine().begin() as conn:
#         stmt = select(analysis).where(analysis.c.analysis_id == analysis_id)
#         result = conn.execute(stmt).mappings().first()
#         if not result:
#             raise HTTPException(status_code=404, detail=f"Analysis with id {analysis_id} not found")
#         component_id = result['component_id']
#         component_ = pipeline_service.find_pipeline_by_id(conn, component_id)
#         if not component_:
#             raise HTTPException(status_code=404, detail=f"Component with id {component_id} not found")
#         try:
#             component_content = json.loads(component_.content)
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=f"Failed to parse component content: {e}")
#         parse_analysis_result_module = component_content.get('parseAnalysisResultModule')
        
#         component_file_list = pipeline_service.find_component_by_parent_id(conn,component_id,"software_output_file")
#         if len(component_file_list) == 0:
#             return {"error":"组件没有添加输出文件,请检查!"}
#             # raise HTTPException(status_code=500, detail=f"组件{component_id}没有添加输出文件,请检查!")
#         component_file_content_list = [{**json.loads(item.content),"component_id":item['component_id']} for item in component_file_list]
#         file_format_list = [
#             {"dir":item['dir'],"fileFormat":item['fileFormat'],"name":item['name'],"component_id":item['component_id']}
#             for item in component_file_content_list if 'fileFormat' in item
#         ]
#         if not file_format_list:
#             return {"error":"组件的输出文件没有配置fileFormat!请检查!"}
#             # raise HTTPException(status_code=500, detail=f"组件{component_id}的输出文件没有配置fileFormat!请检查!")


#         py_module = find_module(component_.namespace,"py_parse_analysis_result",component_id,parse_analysis_result_module,'py')['module']
#         module = importlib.import_module(py_module)
#         parse = getattr(module, "parse")


#         result_dict = {}
#         file_dict={}
#         result_list = []
#         for item in file_format_list:

            
#             # module_dir = component_.pipeline_key
#             # if "moduleDir" in pipeline_content:
#             #     module_dir = pipeline_content['moduleDir']
#             # 递归获取dir_path的文件
        
        
#             dir_path = f"{result['output_dir']}/output/{item['dir']}"
#             get_all_files_recursive(dir_path,item['dir'],file_dict)


#             # if item['module'] not in all_module:
#             #     raise HTTPException(status_code=500, detail=f"py_parse_analysis_result: {module_name}没有找到!")
#             # py_module = all_module[]
            
#             # # parse_result_one()
#             moduleArgs = {}
#             # if "moduleArgs" in item:
#             #     moduleArgs = item['moduleArgs']
            
            
#             res = None    
#             args = {
#                 "dir_path":dir_path,
#                 # "analysis": dict(result),
#                 "file_format":item['fileFormat']
#                 # "args":moduleArgs,
            
#             }
#             res = parse(**args)
            
#             for sub_item in  res:
#                 sub_item.update({
#                     "component_id":item['component_id'],
#                     # "analysis_name":item['name'],
#                     # "analysis_method":item['name'],
#                     "project":result['project'],
#                     "analysis_id":analysis_id,
#                     "analysis_type":"upstream_analysis"
#                     })
#             result_dict.update({item['name']:res})
#             result_list = result_list + res
            
#         if save:
#             sample_name_list = [item['file_name'] for item in result_list]
#             sample_list = sample_service.find_by_sample_name_list(conn,sample_name_list)
#             sample_dict = {item['sample_name']:item for item in sample_list}
#             for item in result_list:
#                 if item['file_name'] in sample_dict:
#                     item['sample_id'] = sample_dict[item['file_name']]['sample_id']
#                 else:
#                     raise HTTPException(status_code=500, detail=f"样本{item['file_name']}不存在!")
#             analysis_result_service.save_or_update_analysis_result_list( conn,result_list)
#             # parse_result_oneV2(res,item['name'],result['project'],"V1.0",analysis_id)
#     return {"result_dict":result_dict,"file_format_list":file_format_list,"file_dict":file_dict}

