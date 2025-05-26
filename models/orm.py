from sqlalchemy import Column, Integer, String
from config.db import Base
from config.db import  engine
from sqlalchemy.dialects.mysql import LONGTEXT

class SampleAnalysisResult(Base):
    __tablename__ = "analysis_result"

    id = Column(Integer, primary_key=True, index=True)
    sample_name = Column(String(255))
    sample_key = Column(String(255))
    analysis_name = Column(String(255))
    analysis_key = Column(String(255))
    analysis_method = Column(String(255))
    software = Column(String(255))
    content = Column(LONGTEXT)
    analysis_version = Column(String(255))
    content_type = Column(String(255))
    project = Column(String(255))
    request_param = Column(LONGTEXT)


    # def __repr__(self):
    #     return user_to_dict(self)

Base.metadata.create_all(bind=engine)
