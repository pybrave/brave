from brave.api.config.db import get_engine
from fastapi import HTTPException
from brave.api.models.core import analysis_result, samples,analysis,t_pipeline_components,t_project
from brave.api.schemas.analysis_result import AnalysisResult,AnalysisResultQuery
from sqlalchemy import and_, desc, select,case
import json
import uuid
from collections import defaultdict

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

def find_analyais_result_groupd_by_component_ids(conn,component_ids,projectList):
    result_dict =  find_analyais_result(conn,AnalysisResultQuery(component_ids=component_ids,projectList=projectList))
    result_dict = [get_analysis_result_metadata(item) for item in result_dict]
            
        # if item["metadata_form"]:
        #     item["metadata_form"] = json.loads(item["metadata_form"])
    grouped = defaultdict(list)
    for item in result_dict:
        item["label"] = item["sample_name"]
        item["value"] = item["id"]
        grouped[item["component_id"]].append(item)
    return grouped

def find_analyais_result(conn,analysisResultQuery:AnalysisResultQuery):
    stmt = analysis_result.select() 
    if analysisResultQuery.querySample:
        stmt =  select(
            analysis_result, 
            samples.c.sample_name,
            # samples.c.sample_group,
            # samples.c.sample_id,
            samples.c.metadata,
            analysis.c.analysis_name,
            t_pipeline_components.c.component_name.label("component_name"),
            # t_pipeline_components.c.label.label("component_label"),
            # t_pipeline_components.c.name.label("analysis_method"),
            t_project.c.project_name.label("project_name")
            # t_project.c.project_id.label("project_id")
            # t_project.c.metadata_form.label("metadata_form")

            ) 
        stmt = stmt.select_from(
            analysis_result.outerjoin(samples,samples.c.sample_id==analysis_result.c.sample_id)
            .outerjoin(analysis,analysis.c.analysis_id==analysis_result.c.analysis_id)
            .outerjoin(t_pipeline_components,t_pipeline_components.c.component_id==analysis_result.c.component_id)
            .outerjoin(t_project,t_project.c.project_id==analysis_result.c.project)
            )
        # stmt = stmt.where(samples.c.project == analysisResultQuery.project)
    # if analysisResultQuery.queryAnalysis:
    #     if not analysisResultQuery.querySample:
    #         stmt = select(analysis_result)
    #     stmt = stmt.add_columns(
    #         analysis.c.analysis_name
    #     )
    #     stmt = stmt.get_final_froms()[0].select_from(analysis_result.outerjoin(analysis,analysis.c.analysis_id==analysis_result.c.analysis_id))
    
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
    if analysisResultQuery.projectList is not None:
        conditions.append(analysis_result.c.project.in_(analysisResultQuery.projectList))


    stmt= stmt.where(and_( *conditions))
    
    if analysisResultQuery.ids :
        case_order = case(
            {id_: index for index, id_ in enumerate(analysisResultQuery.ids)},
            value=analysis_result.c.id,
            else_=len(analysisResultQuery.ids)
        )
        stmt = stmt.order_by(case_order)
    
    if analysisResultQuery.component_ids:
        case_order = case(
            {id_: index for index, id_ in enumerate(analysisResultQuery.component_ids)},
            value=analysis_result.c.component_id,
            else_=len(analysisResultQuery.component_ids)
        )
        stmt = stmt.order_by(case_order)
    
    

    result  = conn.execute(stmt)
    # result = result.fetchall()
    rows = result.mappings().all()
    result_dict = [dict(item) for item in rows ]
    # result_dict = [AnalysisResult(**row) for row in rows]
    # result_dict = []
    for item in result_dict:
        if item['content_type']=="json" and not isinstance(item['content'], dict):
            item['content'] = json.loads(item['content'])
            
        #     result.append(row)
        # # rows = result.mappings().all()
        # pass
    return result_dict

def model_dump_one(item):
    if item.get("content_type")=="json" and  isinstance(item.get("content"), dict):
        if item["metadata"]:
            metadata = json.loads(item["metadata"])
            item = {**metadata,**item}
            del item["metadata"]

        return{
            **{k:v for k,v in item.items() if k!="content"},
            **item['content']
            # 'content':item['content']
        }
    return item

def find_analyais_result_by_ids( conn,value):
    ids = value
    if not isinstance(value,list):
        ids = [value]
    analysis_result = find_analyais_result(conn,AnalysisResultQuery(ids=ids))
    analysis_result = [model_dump_one(item) for item in analysis_result]
    if len(analysis_result)!=len(ids):
        raise HTTPException(status_code=500, detail="数据存在问题!")
    if not isinstance(value,list) and len(analysis_result)==1:
        return analysis_result[0]
    else:
        return analysis_result

def find_analysis_result_exist(conn,component_id,file_name,project):
    stmt = analysis_result.select().where(and_(
        analysis_result.c.component_id == component_id,
        analysis_result.c.file_name == file_name,
        analysis_result.c.project == project
    ))
    result = conn.execute(stmt).mappings().first()
    return result 


            
def add_analysis_result(conn,analysis_result_dict):
    print(f"添加分析结果: {analysis_result_dict['file_name']}")
    analysis_result_dict['analysis_result_id'] = str(uuid.uuid4())
    stmt = analysis_result.insert().values(analysis_result_dict)
    conn.execute(stmt)
def update_analysis_result(conn,analysis_result_id,analysis_result_dict):
    print(f"更新分析结果: {analysis_result_dict['file_name']}")
    stmt = analysis_result.update().where(analysis_result.c.id==analysis_result_id).values(analysis_result_dict)
    conn.execute(stmt)  

def find_by_analysis_result_id(conn,analysis_result_id):
    stmt = analysis_result.select().where(analysis_result.c.analysis_result_id==analysis_result_id)
    result = conn.execute(stmt).mappings().first()
    return result   

def update_sample_id(conn,analysis_result_id,sample_id):
    stmt = analysis_result.update().where(analysis_result.c.analysis_result_id==analysis_result_id).values({"sample_id":sample_id})
    conn.execute(stmt)
        
    
def find_analysis_result_by_analysis_id(conn,analysis_id):
    stmt = analysis_result.select().where(analysis_result.c.analysis_id==analysis_id)
    result = conn.execute(stmt).mappings().all()
    return result

def find_analysis_result_in_analysis_id(conn,analysis_id_list):
    stmt = select(analysis_result)
    # stmt = stmt.select_from(analysis_result.outerjoin(samples,samples.c.sample_id==analysis_result.c.sample_id))
    stmt = stmt.where(analysis_result.c.analysis_id.in_(analysis_id_list))
    result = conn.execute(stmt).mappings().all()
    return result   
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

