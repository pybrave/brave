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
        base_dir = os.getenv("BASE_DIR")
        if not base_dir:
            base_dir= f"{home_dir}/.brave"
            # if not  os.path.exists(default_base_dir):    
            #     os.makedirs(default_base_dir) 

        self.BASE_DIR = Path(base_dir).resolve()# / "data"
        self.BASE_DIR.mkdir(parents=True, exist_ok=True)
        print(f"✅ Using BASE_DIR: {self.BASE_DIR}")


        default_store_dir= f"{base_dir}/store"
        # if not  os.path.exists(default_store_dir):    
        #     os.makedirs(default_store_dir) 
        store_dir = os.getenv("STORE_DIR",default_store_dir)
        self.STORE_DIR = Path(store_dir).resolve()# / "data"
        self.STORE_DIR.mkdir(parents=True, exist_ok=True)
        print(f"✅ Using STORE_DIR: {self.STORE_DIR}")


        default_databases_dir= f"{base_dir}/databases"
        if not  os.path.exists(default_databases_dir):    
            os.makedirs(default_databases_dir) 
        databases_dir = os.getenv("DATABASES_DIR",default_databases_dir)
        self.DATABASES_DIR = Path(databases_dir).resolve()# / "data"
        self.DATABASES_DIR.mkdir(parents=True, exist_ok=True)
        print(f"✅ Using DATABASES_DIR: {self.DATABASES_DIR}")
  
        default_work_dir= f"{base_dir}/work"
        work_dir = os.getenv("WORK_DIR",default_work_dir)
        self.WORK_DIR = Path(work_dir).resolve()# / "data"
        self.WORK_DIR.mkdir(parents=True, exist_ok=True)
        print(f"✅ Using WORK_DIR: {self.WORK_DIR}")

        # pipeline_dir_default = get_pipeline_dir()
       
        default_pipeline_dir = f"{base_dir}/pipeline"
        if not  os.path.exists(default_pipeline_dir):    
            os.makedirs(default_pipeline_dir)    
        pipeline_dir = os.getenv("PIPELINE_DIR",default_pipeline_dir)
        self.PIPELINE_DIR = Path(pipeline_dir).resolve()# / "data"
        # self.WORK_DIR.mkdir(parents=True, exist_ok=True)
        print(f"✅ Using PIPELINE_DIR: {self.PIPELINE_DIR}")
        if pipeline_dir not in sys.path:
            sys.path.insert(0, pipeline_dir)


        default_data_dir = f"{base_dir}"
        data_dir = os.getenv("DATA_DIR",default_data_dir)
        self.DATA_DIR = Path(data_dir).resolve()# / "data"
        # self.WORK_DIR.mkdir(parents=True, exist_ok=True)
        print(f"✅ Using DATA_DIR: {self.DATA_DIR}")
        
        

        default_literature_dir = f"{base_dir}/literature"
        if not  os.path.exists(default_literature_dir):    
            os.makedirs(default_literature_dir)    
        literature_dir = os.getenv("LITERATURE_DIR",default_literature_dir)
        self.LITERATURE_DIR = Path(literature_dir).resolve()# / "data"
        # self.WORK_DIR.mkdir(parents=True, exist_ok=True)
        print(f"✅ Using LITERATURE_DIR: {self.LITERATURE_DIR}")
   

        # 读取数据库配置
        # self.DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()
        # if self.DB_TYPE == "mysql":

        MYSQL_URL = os.getenv("MYSQL_URL")
        if MYSQL_URL:
            # root:123456@192.168.3.60:53306/pipeline
            self.DB_URL = f"mysql+pymysql://{MYSQL_URL}"
        else:
            self.DB_URL = f"sqlite:///{self.BASE_DIR / 'data.db'}"

        print(f"✅ Using DB_URL: {self.DB_URL}")

        self.EXECUTER_TYPE = os.getenv("EXECUTER_TYPE")
        print(f"✅ Using EXECUTER_TYPE: {self.EXECUTER_TYPE}")
        


@lru_cache()
def get_settings() -> Settings:
    """全局共享 Settings 实例"""
    return Settings()


# crud.py
def init(app):
    global _app
    _app = app

def get_graph():
    return _app.state.manager.graph
