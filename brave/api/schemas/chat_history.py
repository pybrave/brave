from typing import Optional
from pydantic import BaseModel

class CreateChatHistory(BaseModel):
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    # chat_history_id: Optional[str] = None
    biz_id: Optional[str] = None
    biz_type: Optional[str] = None
    role: Optional[str] = None
    content: Optional[str] = None
    project_id: Optional[str] = None
    system_prompt: Optional[str] = None
    user_prompt: Optional[str] = None
    thought_chain: Optional[list] = None


class QueryChatHistory(BaseModel):
    chat_history_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    biz_id: Optional[str] = None
    biz_type: Optional[str] = None
    role: Optional[str] = None
    project_id: Optional[str] = None

class ClearChatHistory(BaseModel):
    biz_id: Optional[str] = None
    project_id: Optional[str] = None