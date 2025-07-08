from pydantic import BaseModel

class WriteFile(BaseModel):
    file_path: str
    content: str

