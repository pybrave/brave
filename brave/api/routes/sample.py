from fastapi import APIRouter,Depends
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
def import_sample_form_str(sample:ImportSample):
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
def import_sample_form_str(sample:ImportSample):
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
def import_sample(path):
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
def import_sample(path):
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
def get_analysis(query:SampleGroupQuery):
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
    response_model=List[Sample] )
def list_by_project(project):
    with get_engine().begin() as conn:
        return conn.execute(samples.select() \
            .where(and_(samples.c.project==  project )) ).fetchall()

@sample.get(
    "/list-project",
    tags=['sample'],
    response_model=List[ProjectCount],
    description="列出所有项目")
def list_project():
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