from pydantic import BaseModel

class AddToFile(BaseModel):
    component_id: str
    project: str
    type: str
    path: str