
from brave.api.llm.tool_manager import ToolManager
from brave.api.llm.tools.create_analysis_tools import create_analysis_tools
from brave.api.llm.tools.get_weather import get_weather
from brave.api.llm.tools.log_tools import get_error_log
from brave.api.llm.tools.ui_action import ui_action
def register_tools(tool_manager: ToolManager, sse_service=None):
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
    async def create_analysis_tools_with_runtime_sse(arguments: dict):
        return await create_analysis_tools(arguments, sse_service=sse_service)

    tool_manager.register(
        name="create_analysis_tools",
        func=create_analysis_tools_with_runtime_sse,
        schema={
            "type": "function",
            "function": {
                "name": "create_analysis_tools",
                "strict": "true",
                "description": "根据用户需求创建分析工具。必须传入工具名称 name（例如：箱线图工具）。如果用户只说“创建工具”但未说明用途，先追问用途，再根据用途生成工具名称后调用。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "要创建的工具名称，例如：箱线图工具、PCA降维工具。"
                        }
                    },
                    "required": ["name"],
                    "additionalProperties": "false"
                }
            }
        }
    )

    async def ui_action_with_runtime_sse(arguments: dict):
        return await ui_action(arguments, sse_service=sse_service)

    tool_manager.register(
        name="ui_action",
        func=ui_action_with_runtime_sse,
        schema={
        "type": "function",
        "function": {
                "name": "ui_action",
                "strict": "true",
                "description": "向前端发出 UI 操作指令，例如跳转页面、更新表单、加载表格等。所有 UI 操作必须通过本工具调用。",
                "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                    "type": "string",
                    "enum": [
                        "router.navigate",
                        "table.goto_last_page",
                        "table.goto_page",
                        "form.set_value",
                        "form.submit",
                        "notify.show",
                        "modal.open",
                        "modal.close"
                    ],
                    "description": "要执行的 UI 操作类型。"
                    },
                    "payload": {
                    "type": "object",
                    "description": "根据 action 不同而变化的参数对象。",
                    "properties": {
                        "path": { "type": "string", "description": "router.navigate 使用：跳转路径" },
                        "table_id": { "type": "string", "description": "表格 ID" },
                        "page": { "type": "number", "description": "跳转到指定页（如果需要）" },
                        "message": { "type": "string", "description": "notify.show 使用：提示内容" }
                    },
                    "additionalProperties": True
                    }
                },
                "required": ["action", "payload"],
                "additionalProperties": False
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
