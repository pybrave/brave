from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager

Base = declarative_base()

engine = create_engine("mysql+pymysql://root:123456@192.168.3.60:53306/pipeline", echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

meta = MetaData()

conn = engine.connect()



@contextmanager
def get_db_session():
    db = SessionLocal()
    try:
        yield db
        
    except:
        db.rollback()
        raise
    finally:
        db.close()
