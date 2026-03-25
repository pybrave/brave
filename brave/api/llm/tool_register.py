
from brave.api.llm.tool_manager import ToolManager
from brave.api.llm.tools.create_analysis_tools import create_analysis_tools
from brave.api.llm.tools.get_weather import get_weather
from brave.api.llm.tools.log_tools import get_error_log
def register_tools(tool_manager: ToolManager):
    """注册所有工具到 ToolManager"""

    tool_manager.register(
        name="get_error_log",
        func=get_error_log,
        schema={
            "type": "function",
            "function": {
                "name": "get_error_log",
                "strict": "true",
                "description": "获取指定业务的错误日志，用户需要提供 biz_id 参数",
                "parameters": {
                    "type": "object",
                    "properties": {
                        
                    },
                    "additionalProperties": "false"
                }
            }
        },
#  "获取指定业务的错误日志",
    )

    tool_manager.register(
        name="get_weather",
        func=get_weather,
        schema={
            "type": "function",
            "function": {
                "name": "get_weather",
                "strict": "true",
                "description": "Get weather of a location, the user should supply a location first.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        }
                    },
                    "required": ["location"],
                    "additionalProperties": "false"
                }
            }
        }
    )

    # 创建分析工具,
    tool_manager.register(
        name="create_analysis_tools",
        func=create_analysis_tools,
        schema={
            "type": "function",
            "function": {
                "name": "create_analysis_tools",
                "strict": "true",
                "description": "创建分析工具",
                "parameters": {
                    "type": "object",
                    "properties": {
                    },
                    "additionalProperties": "false"
                }
            }
        }
    )

    # tool_manager.register(
    #     name="create_script_component",
    #     func=component_tools.create_script_component,
    #     description="为tools创建脚本",
    #      parameters={
    #         "type": "object",
    #         "properties": {
    #             "script": {
    #                 "type": "string",
    #                 "description": "LLM 生成的完整脚本内容，必须是可执行或可保存的脚本代码",
    #             },
         
    #         },
    #         "required": ["script"],
    #     },
    # )
