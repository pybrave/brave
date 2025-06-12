# mvp/config.py

import os
from pathlib import Path
from functools import lru_cache

class Settings:
    def __init__(self):
        # 读取 base_dir
        base_dir = os.getenv("MVP_BASE_DIR")
        self.BASE_DIR = Path(base_dir).resolve()# / "data"
        self.BASE_DIR.mkdir(parents=True, exist_ok=True)
        print(f"✅ Using BASE_DIR: {self.BASE_DIR}")

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
