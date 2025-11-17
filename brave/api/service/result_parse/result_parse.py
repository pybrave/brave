import json
from brave.api.core import evenet_bus
from brave.api.core.evenet_bus import EventBus
from brave.api.core.routers_name import RoutersName
from brave.api.schemas.analysis import Analysis
from brave.api.schemas.analysis_result import AnalysisResult, AnalysisResultParseModal
from brave.api.service import analysis_result_service
from brave.api.service import analysis_service
from brave.api.service.analysis_result_parse import AnalysisResultParse
from brave.api.config.db import get_engine
from brave.api.core.event import AnalysisResultEvent
from collections import defaultdict

import asyncio
from typing import  Dict


class ResultParse:
    def __init__(self,analysis_id,evenet_bus:EventBus) -> None:
        self.analysis_id = analysis_id
        self.event_bus = evenet_bus
        self.analysis_result_parse_service = AnalysisResultParse()
        self.analysis_locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

    async def parse(self,save:bool=True):
        async with self.analysis_locks[self.analysis_id]:
            analysis_result_component_id = set()
            with get_engine().begin() as conn:
                params = analysis_service.get_parse_analysis_result_params(conn,self.analysis_id)
                result_list,result_dict = analysis_service.execute_parse(**params)
                # params,result_list,result_dict = self.analysis_result_parse_service.parse_analysis_result(conn,self.analysis_id,True)
                # print("result_list",json.dumps(result_list,indent=4))
                need_add_analysis_result_list = []
                need_update_analysis_result_list = []
                complete_analysis_result_list = []
                for item in result_list:    
                    result = analysis_result_service.find_analysis_result_exist_v2(conn,self.analysis_id,item['component_id'],item['file_name'],item['project'])
                    # result = self.analysis_result_parse_service.find_analysis_result_exist(conn,self.analysis_id,item['component_id'],item['file_name'],item['project'],True)
                    if not result:
                        find_sample = self.analysis_result_parse_service.find_by_sample_name_and_project(conn,item['file_name'],item['project'])
                        if find_sample:
                            item['sample_id'] = find_sample['sample_id']
                        if save:
                            analysis_result_service.add_analysis_result(conn,item)
                        # analsyis = dict(params['analysis'])
                        # analsyis = Analysis(**analsyis)
                        # analysis_result = AnalysisResultParseModal(**item)
                        need_add_analysis_result_list.append(item)
                        # await self.event_bus.dispatch(RoutersName.ANALYSIS_RESULT_ROUTER, AnalysisResultEvent.ON_ANALYSIS_RESULT_ADD, analsyis, analysis_result)
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
                            if save:
                                analysis_result_service.update_analysis_result(conn,result.id,item)
                            # analsyis = dict(params['analysis'])
                            # result = dict(result)
                            # analsyis = Analysis(**analsyis)
                            # analysis_result = AnalysisResultParseModal(**item)
                            need_update_analysis_result_list.append(item)
                        else:
                            complete_analysis_result_list.append(item)

                analsyis = dict(params['analysis'])
                analsyis = Analysis(**analsyis)
                # Deduplication based on analysis_result.component_id
                
                for analysis_result in need_add_analysis_result_list+ complete_analysis_result_list+ need_update_analysis_result_list:
                    if analysis_result["component_id"] not in analysis_result_component_id:
                        analysis_result_component_id.add(analysis_result["component_id"])
                        # analysis_result_modal = AnalysisResultParseModal(
                        #     add_num=len(need_add_analysis_result_list),
                        #     update_num=len(need_update_analysis_result_list),
                        #     complete_num=len(complete_analysis_result_list),
                        #     component_id=analysis_result["component_id"])
                        # await self.event_bus.dispatch(RoutersName.ANALYSIS_RESULT_ROUTER, AnalysisResultEvent.ON_ANALYSIS_RESULT_UPDATE, analsyis, analysis_result_modal)
        
            analysis_result_modal = AnalysisResultParseModal(
                add_num=len(need_add_analysis_result_list),
                update_num=len(need_update_analysis_result_list),
                complete_num=len(complete_analysis_result_list),
                component_ids=list(analysis_result_component_id) )
            await self.event_bus.dispatch(RoutersName.ANALYSIS_RESULT_ROUTER, AnalysisResultEvent.ON_ANALYSIS_RESULT_UPDATE, analsyis, analysis_result_modal)
        
        return result_list,result_dict,params