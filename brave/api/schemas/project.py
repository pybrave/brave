from pydantic import BaseModel
from typing import Optional

class AddProject(BaseModel):
    project_name: str
    metadata_form: str
    research: Optional[str]=None
    description: Optional[str]=None
    parameter: Optional[str]=None

class UpdateProject(BaseModel):
    project_id: str
    project_name: Optional[str]=None
    metadata_form: Optional[str]=None
    research: Optional[str]=None
    description: Optional[str]=None
    parameter: Optional[str]=None