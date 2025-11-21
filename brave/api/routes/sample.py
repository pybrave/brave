import uuid
from fastapi import APIRouter,Depends
from fastapi.params import Body
from sqlalchemy.orm import Session
# from brave.api.config.db import conn
from brave.api.schemas.sample import Sample,SampleGroup,SampleGroupQuery,ImportSample,Sample,ProjectCount
from typing import List
from starlette.status import HTTP_204_NO_CONTENT
from sqlalchemy import func, select
from brave.api.models.orm import SampleAnalysisResult
import glob
import importlib
import os
from brave.api.config.db import get_db_session
from sqlalchemy import and_,or_
import pandas as pd
from brave.api.models.core import samples
from brave.api.config.db import get_engine
from io import StringIO
from fastapi import HTTPException
import json
import math
sample = APIRouter()


def update_or_save_result(db,project,sample_name,file_type,file_path,log_path,verison,analysis_name,software):
        sampleAnalysisResult = db.query(SampleAnalysisResult) \
        .filter(and_(SampleAnalysisResult.analysis_name == analysis_name,\
                SampleAnalysisResult.analysis_verison == verison, \
                SampleAnalysisResult.sample_name == sample_name, \
                SampleAnalysisResult.file_type == file_type, \
                SampleAnalysisResult.project == project \
            )).first()
        if sampleAnalysisResult:
            sampleAnalysisResult.contant_path = file_path
            sampleAnalysisResult.log_path = log_path
            sampleAnalysisResult.software = software
            db.commit()
            db.refresh(sampleAnalysisResult)
            print(">>>>更新: ",file_path,sample_name,file_type,log_path)
        else:
            sampleAnalysisResult = SampleAnalysisResult(analysis_name=analysis_name, \
                analysis_verison=verison, \
                sample_name=sample_name, \
                file_type=file_type, \
                log_path=log_path, \
                software=software, \
                project=project, \
                contant_path=file_path \
                    )
            db.add(sampleAnalysisResult)
            db.commit()
            print(">>>>新增: ",file_path,sample_name,file_type,log_path)


@sample.post("/fast-api/import_sample_form_str",tags=["sample"],)
async def import_sample_form_str(sample:ImportSample):
    csv_buffer = StringIO(sample.content)
    df = pd.read_csv(csv_buffer)
    # pass
    # df = pd.read_csv(path)
    with get_engine().begin() as conn:
        df_dict = df.to_dict(orient="records")
        stmt = samples.insert().values(df_dict)
        conn.execute(stmt)
        # print()
        # return conn.execute(samples.select()).fetchall()
        # print()
        return {"msg":"success"}


@sample.post("/fast-api/update_sample_form_str",tags=["sample"],)
async def import_sample_form_str(sample:ImportSample):
    csv_buffer = StringIO(sample.content)
    df = pd.read_csv(csv_buffer)
    if not "project" in df.columns or not "sample_name" in df.columns:
        raise HTTPException(status_code=500, detail=f"必须包含project和sample_name") 
    with get_engine().begin() as conn:
        df_dict = df.to_dict(orient="records")
        for item in df_dict:
            stmt = samples.update().values(item).where(and_(
                samples.c.project==item['project'],
                samples.c.sample_name==item['sample_name'],
            ) )
            conn.execute(stmt)
        # print()
        # return conn.execute(samples.select()).fetchall()
        # print()
    return {"msg":"success"}

# ,response_model=List[Sample]
# /ssd1/wy/workspace2/leipu/leipu_workspace2/sample/RNA.sample.csv
@sample.get("/import-sample",tags=["sample"],)
async def import_sample(path):
    df = pd.read_csv(path)
    with get_engine().begin() as conn:
        df_dict = df.to_dict(orient="records")
        stmt = samples.insert().values(df_dict)
        conn.execute(stmt)
        # print()
        # return conn.execute(samples.select()).fetchall()
        # print()
        return {"msg":"success"}

@sample.get("/update-import-sample",tags=["sample"],description="更新样本")
async def import_sample(path):
    df = pd.read_csv(path)
    with get_engine().begin() as conn:
        df_dict = df.to_dict(orient="records")
        for item in df_dict:
            stmt = samples.update().values(item).where(samples.c.library_name==item['library_name'])
            conn.execute(stmt)
        # print()
        # return conn.execute(samples.select()).fetchall()
        # print()
        return {"msg":"success"}

@sample.post(
    "/fast-api/find-sample",
    response_model=List[SampleGroup],
    tags=["sample"],
    description="查找样本"
)
async def get_analysis(query:SampleGroupQuery):
    with get_engine().begin() as conn:
        return conn.execute(samples.select() \
            .where(and_(samples.c.project==  query.project \
                ,samples.c.sample_composition==  query.sample_composition \
                ,samples.c.sequencing_target==  query.sequencing_target \
                ,samples.c.sequencing_technique==  query.sequencing_technique \
                )) \
                ).fetchall()

@sample.get(
    "/list-by-project",
    tags=["sample"],
    # response_model=List[Sample] 
    )
async def list_by_project(project):
    with get_engine().begin() as conn:
        result = conn.execute(samples.select() \
            .where(and_(samples.c.project==  project )) ).mappings().all()
        sample_dict = [dict(row) for row in result]
        result_dict = []
        for item in sample_dict:
            if item['metadata']:
                # item['metadata'] = 
                try:
                    metadata = json.loads(item['metadata'])
                    metadata = {k:v for k,v in metadata.items() if not  (isinstance(v, float) and math.isnan(v)) }
                    result_dict.append({**metadata,**{k:v for k,v in item.items() if k!="metadata"}})
                    pass
                except Exception as e:
                    # e.with_traceback()
                    print(e)
                    result_dict.append(item)
            else:
                result_dict.append(item)
            # else:
            #     item['metadata'] = {}
    sample_names = [ item['sample_name'] for item in result_dict]
    if not is_unique(sample_names):
        raise HTTPException(status_code=500, detail=f"data error: sample_name not unique in project {project}")

    return result_dict

@sample.get(
    "/list-project",
    tags=['sample'],
    response_model=List[ProjectCount],
    description="列出所有项目")
async def list_project():
    with get_engine().begin() as conn:
        stmt = (
            select(
                samples.c.project,
                func.count(samples.c.id).label("count")
            )
            .group_by(samples.c.project)
        )
        result = conn.execute(stmt).fetchall()
        # data = [dict(row._mapping) for row in result.fetchall()]
        return result
def is_unique(lst):
    return len(lst) == len(set(lst))

def find_sample_name_by_project_id(conn,project_id):
    stmt = select(samples.c.sample_name).where(samples.c.project==project_id)
    result = conn.execute(stmt).mappings().all()
    sample_name_list = [ item.sample_name for item in result]
    return sample_name_list


@sample.post(
    "/batch-update-sample",
    tags=["sample"],
    description="batch save sample"
)
async def batchSave(importSample:ImportSample):
    df = pd.read_csv(StringIO(importSample.content), sep="\t")
    df_dict = df.to_dict(orient="records")
    sample_list = [build_metadata(item) for item in df_dict]

    sample_name_list = [ item['sample_name'] for item in df_dict]
    if is_unique(sample_name_list) is False:
        raise HTTPException(status_code=500, detail=f"data error: sample_name not unique in project {importSample.project_id}")

    with get_engine().begin() as conn:
        # update sample by sample_id
        for item in sample_list:
            stmt = samples.update().values(item).where(and_(
                samples.c.sample_id==item['sample_id'],
                samples.c.project==importSample.project_id
            ))
            result = conn.execute(stmt)
        return {"msg":"success"}


@sample.post(
    "/batch-create-sample",
    tags=["sample"],
    description="batch create sample"
)
async def batchCreate(importSample:ImportSample):
    df = pd.read_csv(StringIO(importSample.content), sep="\t")
    df_dict = df.to_dict(orient="records")
    sample_names = [ item['sample_name'] for item in df_dict]

    sample_list = [build_metadata(item, create_new=True) for item in df_dict]
    with get_engine().begin() as conn:
        db_sample_names = find_sample_name_by_project_id(conn,importSample.project_id)
        sample_names = sample_names +db_sample_names
        if is_unique(sample_names) is False:
            raise HTTPException(status_code=500, detail=f"data error: sample_name not unique in project {importSample.project_id}")
        
        # update sample by sample_id
        for item in sample_list:
            stmt = samples.insert().values({**item, 'project':importSample.project_id})
            result = conn.execute(stmt)
        return {"msg":"success"}



def build_metadata(sample:dict,create_new:bool=False):
    new_dict ={}
    metadata = {k:v for k,v in sample.items() if k not in ['sample_id','sample_name'] and v is not None and not  (isinstance(v, float) and math.isnan(v))}
    new_dict['metadata'] = json.dumps(metadata)
    if create_new:
        str_uuid = str(uuid.uuid4())
        new_dict['sample_id'] =str_uuid
    else:
        new_dict['sample_id'] = sample['sample_id']
    new_dict['sample_name'] = sample['sample_name']
    return new_dict
