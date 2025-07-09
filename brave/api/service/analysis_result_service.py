from brave.api.config.db import get_engine
from fastapi import HTTPException
from brave.api.models.core import analysis_result, samples
from brave.api.schemas.analysis_result import AnalysisResult,AnalysisResultQuery
from sqlalchemy import and_, select
import json

def find_analyais_result(conn,analysisResultQuery:AnalysisResultQuery):
    stmt = analysis_result.select() 
    if analysisResultQuery.querySample:
        stmt =  select(analysis_result, samples).select_from(analysis_result.outerjoin(samples,samples.c.sample_key==analysis_result.c.analysis_key))
    
    conditions = []
    if analysisResultQuery.project is not None:
        conditions.append(analysis_result.c.project == analysisResultQuery.project)
    if analysisResultQuery.ids is not None:
        conditions.append(analysis_result.c.id.in_(analysisResultQuery.ids))
    if analysisResultQuery.analysis_method is not None:
        conditions.append(analysis_result.c.analysis_method.in_(analysisResultQuery.analysis_method))
    if analysisResultQuery.analysis_type is not None:
        conditions.append(analysis_result.c.analysis_type == analysisResultQuery.analysis_type)
    if analysisResultQuery.component_ids is not None:
        conditions.append(analysis_result.c.component_id.in_(analysisResultQuery.component_ids))
    if analysisResultQuery.component_id is not None:
        conditions.append(analysis_result.c.component_id == analysisResultQuery.component_id)
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



def save_or_update_analysis_result_list(conn, analysis_result_list):
    for item in analysis_result_list:
        stmt = analysis_result.select().where(and_(
            analysis_result.c.component_id == item['component_id'],
            analysis_result.c.analysis_key == item['analysis_key'],
            analysis_result.c.project == item['project']
        ))
        result = conn.execute(stmt).mappings().first()
        if result:
            stmt = analysis_result.update().where(analysis_result.c.id == result.id).values(item)
            conn.execute(stmt)
        else:
            stmt = analysis_result.insert().values(item)
            conn.execute(stmt)
            



        
    # with get_db_session() as db:
    #     if len(res) >0:
    #         # print(res[0])
    #         if len(res[0]) == 4:
    #             for analysis_key,software,content_type,content in res:
    #                 update_or_save_result(analysis_key,analysis_key, software, content_type, content, db, project, verison, analysis_method,analysis_name,analysis_id)
    #         elif len(res[0]) == 5:
    #             for analysis_key,sample_name,software,content_type,content in res:
    #                 update_or_save_result(analysis_key,sample_name, software, content_type, content, db, project, verison, analysis_method,analysis_name,analysis_id)


# def update_or_save_result(analysis_key,sample_name, software, content_type, content, db, project, verison, analysis_method,analysis_name,analysis_id):
#         sampleAnalysisResult = db.query(SampleAnalysisResult) \
#         .filter(and_(SampleAnalysisResult.analysis_method == analysis_method,\
#                 SampleAnalysisResult.analysis_version == verison, \
#                 SampleAnalysisResult.analysis_key == analysis_key, \
#                 SampleAnalysisResult.project == project \
#             )).first()
#         if sampleAnalysisResult:
#             sampleAnalysisResult.sample_name = sample_name
#             sampleAnalysisResult.content = content
#             sampleAnalysisResult.sample_key=sample_name
#             sampleAnalysisResult.content_type = content_type
#             sampleAnalysisResult.analysis_name = analysis_name
#             sampleAnalysisResult.analysis_id = analysis_id
#             sampleAnalysisResult.analysis_type="upstream"
#             # sampleAnalysisResult.log_path = log_path
#             sampleAnalysisResult.software = software
#             db.commit()
#             db.refresh(sampleAnalysisResult)
#             print(">>>>更新: ",sample_name, software, content_type)
#         else:
#             sampleAnalysisResult = SampleAnalysisResult(analysis_method=analysis_method, \
#                 analysis_version=verison, \
#                 sample_name=sample_name, \
#                 content_type=content_type, \
#                 analysis_name=analysis_name, \
#                 analysis_key=analysis_key, \
#                 analysis_id=analysis_id, \
#                 analysis_type="upstream", \
#                 # log_path=log_path, \
#                 software=software, \
#                 project=project, \
#                 sample_key=sample_name, \
#                 content=content \
#                     )
#             db.add(sampleAnalysisResult)
#             db.commit()
#             print(">>>>新增: ",sample_name, software, content_type)

