import uuid
from brave.api.schemas.chat_history import CreateChatHistory, QueryChatHistory
from brave.api.models.core import t_chat_history
from sqlalchemy import func, select


# instert t_chat_history use core
def insert_chat_history(conn, createChatHistory: CreateChatHistory):
    str_uuid = str(uuid.uuid4())
    params = createChatHistory.model_dump()
    params = {k: v for k, v in params.items() if v is not None}
    params["chat_history_id"] = str_uuid
    stmt = t_chat_history.insert().values(**params)
    conn.execute(stmt)
    conn.commit()

def get_chat_history_by_project_id_and_biz_id(conn, query: QueryChatHistory):
    project_id = query.project_id
    biz_id = query.biz_id
    stmt = select(
        t_chat_history
    )
    stmt = stmt.where(
        t_chat_history.c.project_id == project_id,
        t_chat_history.c.biz_id == biz_id
    ).order_by(t_chat_history.c.created_at.asc())

    result = conn.execute(stmt).all()
    return result