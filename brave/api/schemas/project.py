from pydantic import BaseModel

class AddProject(BaseModel):
    project_name: str
    metadata_form: str

class UpdateProject(BaseModel):
    project_id: str
    project_name: str
    metadata_form: str