# mvp/config.py

import os
from pathlib import Path
from functools import lru_cache

class Settings:
    def __init__(self):
        # 读取 base_dir
        base_dir = os.getenv("MVP_BASE_DIR",os.getcwd())
        self.BASE_DIR = Path(base_dir).resolve()# / "data"
        self.BASE_DIR.mkdir(parents=True, exist_ok=True)
        print(f"✅ Using BASE_DIR: {self.BASE_DIR}")

        work_dir = os.getenv("WORK_DIR",base_dir)
        self.WORK_DIR = Path(work_dir).resolve()# / "data"
        self.WORK_DIR.mkdir(parents=True, exist_ok=True)
        print(f"✅ Using WORK_DIR: {self.WORK_DIR}")


        # 读取数据库配置
        self.DB_TYPE = os.getenv("DB_TYPE", "mysql").lower()
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
