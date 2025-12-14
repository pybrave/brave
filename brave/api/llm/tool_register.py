
from brave.api.llm.tool_manager import ToolManager
from brave.api.llm.tools.log_tools import get_error_log


def register_tools(tool_manager: ToolManager):
    """注册所有工具到 ToolManager"""

    tool_manager.register(
        name="get_error_log",
        func=get_error_log,
        description="获取指定业务的错误日志",
        parameters={
            # "type": "object",
            # "properties": {
            #     # "biz_id": {
            #     #     "type": "string",
            #     #     "description": "业务ID，比如工作流ID或任务ID",
            #     # },
            #     # "biz_type": {
            #     #     "type": "string",
            #     #     "description": "业务类型，比如'workflow'或'task'",
            #     # },
            # },
            # "required": ["biz_id", "biz_type"],
        },
    )