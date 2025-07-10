from sqlalchemy import Column, Integer, String
from brave.api.config.db import Base
# from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy import Text

class SampleAnalysisResult(Base):
    __tablename__ = "analysis_result"

    id = Column(Integer, primary_key=True, index=True)
    sample_name = Column(String(255))
    sample_id = Column(String(255))
    # sample_key = Column(String(255))
    # analysis_name = Column(String(255))
    analysis_key = Column(String(255))
    component_id = Column(String(255))
    analysis_method = Column(String(255))
    software = Column(String(255))
    content = Column(Text)
    analysis_id = Column(String(255))
    analysis_version = Column(String(255))
    content_type = Column(String(255))
    project = Column(String(255))
    request_param = Column(Text)
    analysis_type = Column(String(255))
    create_date = Column(String(255))


    # def __repr__(self):
    #     return user_to_dict(self)


# class Sample(Base):
#     __tablename__ = "t_samples"

#     id = Column(Integer, primary_key=True, index=True)
#     sample_name = Column(String(255))
#     sample_key = Column(String(255))
#     sample_group= Column(String(255))

# Base.metadata.create_all(bind=engine)
