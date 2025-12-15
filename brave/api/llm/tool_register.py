
from brave.api.llm.tool_manager import ToolManager
from brave.api.llm.tools.log_tools import get_error_log

from .tools import component_tools

def register_tools(tool_manager: ToolManager):
    """注册所有工具到 ToolManager"""

    tool_manager.register(
        name="get_error_log",
        func=get_error_log,
        description="获取指定业务的错误日志",
        # parameters={
        #     # "type": "object",
        #     # "properties": {
        #     #     # "biz_id": {
        #     #     #     "type": "string",
        #     #     #     "description": "业务ID，比如工作流ID或任务ID",
        #     #     # },
        #     #     # "biz_type": {
        #     #     #     "type": "string",
        #     #     #     "description": "业务类型，比如'workflow'或'task'",
        #     #     # },
        #     # },
        #     # "required": ["biz_id", "biz_type"],
        # },
    )

    tool_manager.register(
        name="create_script_component",
        func=component_tools.create_script_component,
        description="为tools创建脚本",
         parameters={
            "type": "object",
            "properties": {
                "script": {
                    "type": "string",
                    "description": "LLM 生成的完整脚本内容，必须是可执行或可保存的脚本代码",
                },
         
            },
            "required": ["script"],
        },
    )