# brave/config.py

import os
from pathlib import Path
from functools import lru_cache
from importlib.resources import files
import sys
from pathlib import Path

# def get_pipeline_dir():
#     pipeline_config_path = str(files("brave.pipeline").joinpath("config.json"))
#     pipeline_dir = os.path.dirname(pipeline_config_path)
#     return  pipeline_dir
class Settings:
    def __init__(self):
        # 读取 base_dir
        home_dir = Path.home()
        
        default_base_dir= f"{home_dir}/.brave/base_dir"
        if not  os.path.exists(default_base_dir):    
            os.makedirs(default_base_dir) 
        base_dir = os.getenv("BASE_DIR",default_base_dir)
        self.BASE_DIR = Path(base_dir).resolve()# / "data"
        self.BASE_DIR.mkdir(parents=True, exist_ok=True)
        print(f"✅ Using BASE_DIR: {self.BASE_DIR}")

        default_databases_dir= f"{home_dir}/.brave/databases"
        if not  os.path.exists(default_databases_dir):    
            os.makedirs(default_databases_dir) 
        databases_dir = os.getenv("DATABASES_DIR",default_databases_dir)
        self.DATABASES_DIR = Path(databases_dir).resolve()# / "data"
        self.DATABASES_DIR.mkdir(parents=True, exist_ok=True)
        print(f"✅ Using DATABASES_DIR: {self.DATABASES_DIR}")
  

        work_dir = os.getenv("WORK_DIR",default_base_dir)
        self.WORK_DIR = Path(work_dir).resolve()# / "data"
        self.WORK_DIR.mkdir(parents=True, exist_ok=True)
        print(f"✅ Using WORK_DIR: {self.WORK_DIR}")

        # pipeline_dir_default = get_pipeline_dir()
       
        default_pipeline_dir = f"{home_dir}/.brave/pipeline"
        if not  os.path.exists(default_pipeline_dir):    
            os.makedirs(default_pipeline_dir)    
        pipeline_dir = os.getenv("PIPELINE_DIR",default_pipeline_dir)
        self.PIPELINE_DIR = Path(pipeline_dir).resolve()# / "data"
        # self.WORK_DIR.mkdir(parents=True, exist_ok=True)
        print(f"✅ Using PIPELINE_DIR: {self.PIPELINE_DIR}")
        if pipeline_dir not in sys.path:
            sys.path.insert(0, pipeline_dir)

        default_literature_dir = f"{home_dir}/.brave/literature"
        if not  os.path.exists(default_literature_dir):    
            os.makedirs(default_literature_dir)    
        literature_dir = os.getenv("LITERATURE_DIR",default_literature_dir)
        self.LITERATURE_DIR = Path(literature_dir).resolve()# / "data"
        # self.WORK_DIR.mkdir(parents=True, exist_ok=True)
        print(f"✅ Using LITERATURE_DIR: {self.LITERATURE_DIR}")
        # downstream_analysis_result = self.BASE_DIR / "downstream_analysis_result"
        # downstream_analysis_result.mkdir(parents=True, exist_ok=True)
        # self.DOWNSTREAM_ANALYSIS_RESULT_DIR = downstream_analysis_result
        # print(f"✅ Using DOWNSTREAM_ANALYSIS_RESULT_DIR: {self.DOWNSTREAM_ANALYSIS_RESULT_DIR}")


        # 读取数据库配置
        self.DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()
        if self.DB_TYPE == "mysql":
            MYSQL_URL = os.getenv("MYSQL_URL")
            self.DB_URL = f"mysql+pymysql://{MYSQL_URL}"
        else:
            self.DB_URL = f"sqlite:///{self.BASE_DIR / 'data.db'}"

        print(f"✅ Using DB_URL: {self.DB_URL}")

        


@lru_cache()
def get_settings() -> Settings:
    """全局共享 Settings 实例"""
    return Settings()
