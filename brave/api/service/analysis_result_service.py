from brave.api.config.db import get_engine
from fastapi import HTTPException
from brave.api.models.core import analysis_result, samples
from brave.api.schemas.analysis_result import AnalysisResult,AnalysisResultQuery
from sqlalchemy import and_, select
import json

def find_analyais_result(conn,analysisResultQuery:AnalysisResultQuery):
    stmt = analysis_result.select() 
    if analysisResultQuery.querySample:
        stmt =  select(analysis_result, samples).select_from(analysis_result.outerjoin(samples,samples.c.sample_key==analysis_result.c.sample_key))
    
    conditions = []
    if analysisResultQuery.project is not None:
        conditions.append(analysis_result.c.project == analysisResultQuery.project)
    if analysisResultQuery.ids is not None:
        conditions.append(analysis_result.c.id.in_(analysisResultQuery.ids))
    if analysisResultQuery.analysis_method is not None:
        conditions.append(analysis_result.c.analysis_method.in_(analysisResultQuery.analysis_method))
    if analysisResultQuery.analysis_type is not None:
        conditions.append(analysis_result.c.analysis_type == analysisResultQuery.analysis_type)
    stmt= stmt.where(and_( *conditions))
    
    result  = conn.execute(stmt)
    # result = result.fetchall()
    rows = result.mappings().all()
    result_dict = [AnalysisResult(**row) for row in rows]
    # result_dict = []
    for item in result_dict:
        if item.content_type=="json" and not isinstance(item.content, dict):
            item.content = json.loads(item.content)
        #     result.append(row)
        # # rows = result.mappings().all()
        # pass
    return result_dict

def model_dump_one(item):
    if item.get("content_type")=="json" and  isinstance(item.get("content"), dict):
        return{
            **{k:v for k,v in item.items() if k!="content"},
            **item['content']
        }
    return item

def find_analyais_result_by_ids( conn,value):
    ids = value
    if not isinstance(value,list):
        ids = [value]
    analysis_result = find_analyais_result(conn,AnalysisResultQuery(ids=ids))
    analysis_result = [model_dump_one(item.model_dump()) for item in analysis_result]
    if len(analysis_result)!=len(ids):
        raise HTTPException(status_code=500, detail="数据存在问题!")
    if not isinstance(value,list) and len(analysis_result)==1:
        return analysis_result[0]
    else:
        return analysis_result