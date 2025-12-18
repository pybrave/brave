import brave.api.service.analysis_service as analysis_service
from brave.api.config.db import get_engine
import os


def tail(file_path, n=80, encoding="utf-8"):
    if not os.path.exists(file_path):
        return ""

    with open(file_path, "rb") as f:
        f.seek(0, os.SEEK_END)
        buffer = bytearray()
        pointer = f.tell()

        while pointer > 0 and buffer.count(b"\n") <= n:
            step = min(1024, pointer)
            pointer -= step
            f.seek(pointer)
            buffer[:0] = f.read(step)

        return b"\n".join(buffer.splitlines()[-n:]).decode(
            encoding, errors="ignore"
        )
async def get_error_log(arguments: dict):
    # 这里写你自己的逻辑
    # data = f"模拟获取日志内容{biz_id}-{biz_type}"
    # print(f"获取日志: {biz_id}, {biz_type}")
    if "biz_id" not in arguments:
        return "缺少参数 biz_id"
    biz_id = arguments["biz_id"]
    data = ""
    with get_engine().begin() as conn:
        analysis = analysis_service.find_analysis_by_id(conn,biz_id)
    
    if not analysis:
        return "未查询到日志"
    executor_log_file = analysis["command_log_path"]
    if os.path.exists(executor_log_file):
        # with open(executor_log_file, 'r') as f:
        #     data = f.read()
        tail_lines = tail(executor_log_file, n=80)
        data += f"任务执行日志最后80行内容:\n{tail_lines}\n"
    else:
        data += "任务执行日志文件不存在\n"
        
    return data or "未查询到日志"