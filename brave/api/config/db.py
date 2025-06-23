from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
import os
from brave.api.config.config import get_settings
import threading


# BASE_DIR = os.path.join(BASE_DIR, 'data')
# if not os.path.exists(BASE_DIR):
#     os.makedirs(BASE_DIR)
# print(f"Using BASE_DIR: {BASE_DIR}")
# DB_TYPE = os.getenv("DB_TYPE", "sqlite")  # "sqlite" or "mysql"
# if DB_TYPE == "mysql":
#     DB_URL = os.getenv("MYSQL_URL", "mysql+pymysql://root:123456@192.168.3.60:53306/pipeline")
# else:
#     # BASE_DIR = os.path.dirname(__file__)
#     DB_URL = f"sqlite:///{os.path.join(BASE_DIR, 'data.db')}"


# engine =  create_engine(DB_URL, echo=False)
# # engine = create_engine("mysql+pymysql://root:123456@192.168.3.60:53306/pipeline", echo=False)
# SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
meta = MetaData()
Base = declarative_base()
# class DbEngine:
#     def __init__(self):
# engine =  None
# SessionLocal = None
# engine_dict = {}

# 线程安全的 Engine 单例
class EngineSingleton:
    _engine = None
    _lock = threading.Lock()

    @classmethod
    def get_engine(cls):
        if cls._engine is None:
            with cls._lock:
                if cls._engine is None:  # 双重检查锁
                    settings = get_settings()

                    # cls._engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
                    cls._engine = create_engine(settings.DB_URL, echo=False, future=True)
        return cls._engine

# conn = engine.connect()
def init_engine():
    # global engine, SessionLocal
    # engine = create_engine(db_url, echo=False, future=True)
    engine = EngineSingleton.get_engine()
    
    # engine_dict.update({"aaa":"123"})
    return engine
    

def get_engine():
    engine = init_engine()
    return engine 



@contextmanager
def get_db_session():
    settings = get_settings()
    engine = init_engine()
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    db = SessionLocal()
    
    try:
        yield db
        
    except:
        db.rollback()
        raise
    finally:
        db.close()
 