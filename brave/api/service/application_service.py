from brave.api.config.db import get_engine
from brave.api.models.core import t_application


async def list_application(conn):
    result = conn.execute(t_application.select())
    return result.mappings().all()