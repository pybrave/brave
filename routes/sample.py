from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from config.db import conn
from schemas.sample import Sample
from typing import List
from starlette.status import HTTP_204_NO_CONTENT
from sqlalchemy import func, select
from config.db import SessionLocal
from cryptography.fernet import Fernet
from models.orm import SampleAnalysisResult
import glob
import importlib
import os
from config.db import get_db_session
from sqlalchemy import and_,or_
import pandas as pd
from models.core import samples
from config.db import engine


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


# ,response_model=List[Sample]
@sample.get("/import-sample")
def import_sample(path):
    df = pd.read_csv(path)
    with engine.begin() as conn:
        df_dict = df.to_dict(orient="records")
        stmt = samples.insert().values(df_dict)
        conn.execute(stmt)
        # print()
        # return conn.execute(samples.select()).fetchall()
        # print()
        return {"msg":"success"}

@sample.get("/update-import-sample")
def import_sample(path):
    df = pd.read_csv(path)
    with engine.begin() as conn:
        df_dict = df.to_dict(orient="records")
        for item in df_dict:
            stmt = samples.update().values(item).where(samples.c.library_name==item['library_name'])
            conn.execute(stmt)
        # print()
        # return conn.execute(samples.select()).fetchall()
        # print()
        return {"msg":"success"}