from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    biz_id: str = None
    biz_type: str = None
    project_id: str = None
    is_save_prompt: bool = False
