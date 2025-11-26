import os
from brave.api.config.config import get_settings
from brave.api.config.db import get_engine
from fastapi import HTTPException
from brave.api.models.core import analysis_result, samples,analysis,t_pipeline_components,t_project
from brave.api.schemas.analysis_result import AnalysisResult,AnalysisResultQuery
from sqlalchemy import and_, desc, select,case,or_
from brave.api.service import sample_service
import json
import uuid
from collections import defaultdict
import pandas as pd
import brave.api.service.pipeline as pipeline_service


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

def find_analyais_result_groupd_by_component_ids(conn,component_ids,projectList):
    grouped =  find_analysis_result_grouped(conn,AnalysisResultQuery(component_ids=component_ids,projectList=projectList))
    # result_dict = [get_analysis_result_metadata(item) for item in result_dict]
            

    # grouped = defaultdict(list)
    # for item in result_dict:
    #     item["label"] = item["sample_name"] or item.get("file_name","")
    #     item["value"] = item["id"]
    #     grouped[item["component_id"]].append(item)
    return grouped

def find_analysis_result_grouped(conn,analysisResultQuery:AnalysisResultQuery):
    component_dict = {}
    component_list = pipeline_service.find_by_component_ids(conn,analysisResultQuery.component_ids)
    component_ids = set()
    for item in  component_list:
        if item.get("component_ids"):
            ids = json.loads( item["component_ids"])
            component_ids.update(ids)
            for id in ids:
                component_dict[id] = item["component_id"]
        else:
            component_ids.add(item["component_id"])

    analysisResultQuery.component_ids = list(component_ids)
    result_dict = find_analyais_result(conn,analysisResultQuery)
    result_dict = [get_analysis_result_metadata(item) for item in result_dict]
            

    grouped = defaultdict(list)
    for item in result_dict:
        item["label"] = item["sample_name"] or item.get("file_name","")
        item["value"] = item["id"]
        if item["component_id"] in component_dict:
            query_component_id = component_dict[item["component_id"]]
            grouped[query_component_id].append(item)
        else:
            grouped[item["component_id"]].append(item)
        
    for item in analysisResultQuery.component_ids:
        if item not in grouped:
            grouped[item] = []

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
            analysis.c.used,
            t_pipeline_components.c.component_name.label("component_name"),
            t_pipeline_components.c.file_type.label("file_type"),
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
    # conditions.append(analysis.c.used==True)
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
    if analysisResultQuery.analsyis_id is not None:
        conditions.append(analysis_result.c.analysis_id == analysisResultQuery.analsyis_id)

    #  (nextflow.used = TRUE OR nextflow.analysis_id IS NULL)
    stmt= stmt.where(and_( *conditions, or_(analysis.c.used == True, analysis.c.analysis_id == None)))

    
    
    # if analysisResultQuery.ids :
    #     case_order = case(
    #         {id_: index for index, id_ in enumerate(analysisResultQuery.ids)},
    #         value=analysis_result.c.id,
    #         else_=len(analysisResultQuery.ids)
    #     )
    #     stmt = stmt.order_by(case_order)
    
    # if analysisResultQuery.component_ids:
    #     case_order = case(
    #         {id_: index for index, id_ in enumerate(analysisResultQuery.component_ids)},
    #         value=analysis_result.c.component_id,
    #         else_=len(analysisResultQuery.component_ids)
    #     )
    #     stmt = stmt.order_by(case_order)
    
    stmt = stmt.order_by(desc(analysis_result.c.id))

    result  = conn.execute(stmt)
    # result = result.fetchall()
    rows = result.mappings().all()
    result_dict = [dict(item) for item in rows ]
    # result_dict = [AnalysisResult(**row) for row in rows]
    file_type_list = [item for item in result_dict if item.get("file_type") and item.get("file_type")=="collected"]
    samples_dict = {}
    if len(file_type_list)>0:
        if analysisResultQuery.projectList:
            samples_list = sample_service.find_by_project_in_list(conn,analysisResultQuery.projectList)
        else:
            samples_list = sample_service.find_by_project(conn,analysisResultQuery.project)
        samples_dict = { sample["sample_name"]:sample for sample in samples_list}

    settings = get_settings()
    data_dir = settings.DATA_DIR
    for index in range(len(result_dict)):
        item = result_dict[index]
        df_content = pd.DataFrame()
        if item['content_type']=="json" and not isinstance(item['content'], dict) and item['file_type']!="collected":
            try:
                item['content'] = json.loads(item['content'])
            except:
                pass
        elif analysisResultQuery.build_collected:
            content = item['content']
            if not os.path.exists(content):
                continue
            df_content = pd.read_csv(content,sep="\t")
            df_colnames = df_content.columns
            df_colnames = [build_collected_analysis_result(column,item, samples_dict) for column in df_colnames]
            item['columns'] = df_colnames
            data_suffix = item["content"].replace(str(data_dir),"")
            item["url"] = f"/brave-api/data-dir{data_suffix}"
            

        if analysisResultQuery.build_collected_rows and analysisResultQuery.rows:
            if analysisResultQuery.rows !=-1:
                df_content = df_content.head(analysisResultQuery.rows)
            item['rows'] = json.loads(df_content.to_json(orient="values"))

            
            
        #     result.append(row)
        # # rows = result.mappings().all()
        # pass
    return result_dict




def build_collected_analysis_result(column,analsyis_result,samples_dict):

    sample = samples_dict.get(column)
    if sample:
        sample = dict(sample)
        del sample["id"]
        # sample["sample_source"] = analsyis_result.get("sample_source")
        sample = get_analysis_result_metadata(sample)
        return {"id":analsyis_result.get("id"),
            "analysis_result_id":analsyis_result.get("analysis_result_id"),
            "columns_name":column,**sample}
    
    return {"id":analsyis_result.get("id"),
            "sample_name":column,
            "analysis_result_id":analsyis_result.get("analysis_result_id"),
            "columns_name":column}

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
    analysis_result = find_analyais_result(conn,AnalysisResultQuery(ids=ids,build_collected=False))
    analysis_result = [model_dump_one(item) for item in analysis_result]
    if len(analysis_result)!=len(ids):
        raise HTTPException(status_code=500, detail="数据存在问题!")
    # if not isinstance(value,list) and len(analysis_result)==1:
    #     return analysis_result[0]
    # else:
    return analysis_result

def find_analysis_result_exist(conn,component_id,file_name,project):
    stmt = analysis_result.select().where(and_(
        analysis_result.c.component_id == component_id,
        analysis_result.c.file_name == file_name,
        analysis_result.c.project == project
    ))
    result = conn.execute(stmt).mappings().first()
    return result 


def find_analysis_result_exist_v2(conn, analysis_id,component_id,file_name,project):
    stmt = analysis_result.select().where(and_(
        analysis_result.c.analysis_id == analysis_id,
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

