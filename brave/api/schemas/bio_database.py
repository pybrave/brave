from typing import Optional
from pydantic import BaseModel

class QueryBiodatabase(BaseModel):
    database_id:Optional[str] = None
    name:Optional[str] = None
    path:Optional[str] = None
    type:Optional[str] = None
    type_list:Optional[list[str]] = None

class AddBioDatabase(BaseModel):
    name:str
    path:str
    db_index:Optional[str] = None
    type:str

class UpdateBioDatabase(BaseModel):
    database_id:str
    name:Optional[str] = None
    path:Optional[str] = None
    type:Optional[str] = None
    db_index:Optional[str] = None