import brave.api.service.analysis_service as analysis_service
from brave.api.config.db import get_engine
import os

async def get_error_log(biz_id: str):
    # 这里写你自己的逻辑
    # data = f"模拟获取日志内容{biz_id}-{biz_type}"
    # print(f"获取日志: {biz_id}, {biz_type}")
    data = ""
    with get_engine().begin() as conn:
        analysis = analysis_service.find_analysis_by_id(conn,biz_id)
    
    if not analysis:
        return "未查询到日志"
    executor_log_file = analysis["command_log_path"]
    if os.path.exists(executor_log_file):
        with open(executor_log_file, 'r') as f:
            data = f.read()
        
    return data or "未查询到日志"