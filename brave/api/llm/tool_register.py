
from brave.api.llm.tool_manager import ToolManager
from brave.api.llm.tools.add_example import add_example
from brave.api.llm.tools.update_analysis_script_from import update_analysis_script_from
from brave.api.llm.tools.create_analysis_script import create_analysis_script
from brave.api.llm.tools.create_analysis_tools import create_analysis_tools
from brave.api.llm.tools.get_weather import get_weather
from brave.api.llm.tools.log_tools import get_error_log
from brave.api.llm.tools.ui_action import ui_action
from brave.api.llm.tools.update_analysis_script import update_analysis_script
def register_tools(tool_manager: ToolManager, sse_service=None):
    """注册所有工具到 ToolManager"""

    tool_manager.register(
        name="get_error_log",
        func=get_error_log,
        schema={
            "type": "function",
            "function": {
                "name": "get_error_log",
                "strict": True,
                "description": "获取指定业务的错误日志，用户需要提供 biz_id 参数",
                "parameters": {
                    "type": "object",
                    "properties": {
                        
                    },
                    "additionalProperties": False
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
                "strict": True,
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
                    "additionalProperties": False
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
                "strict": True,
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
                    "additionalProperties": False
                }
            }
        }
    )
    

    tool_manager.register(
        name="create_analysis_script",
        func=create_analysis_script,
        schema={
            "type": "function",
            "function": {
                "name": "create_analysis_script",
                "strict": True,
                "description": "根据用户需求创建分析脚本。必须传入脚本名称 name（例如：箱线图脚本）。如果用户只说“创建脚本”但未说明用途，先追问用途，再根据用途生成脚本名称后调用。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "要创建的脚本名称，例如：箱线图脚本、PCA降维脚本。"
                        },"tools_id": {
                            "type": "string",
                            "description": "工具 ID，用于关联到具体工具。"
                        }
                    },
                    "required": ["name", "tools_id"],
                    "additionalProperties": False
                }
            }
        }
    )

    tool_manager.register(
        name="update_analysis_script",
        func=update_analysis_script,
        schema={
            "type": "function",
            "function": {
                "name": "update_analysis_script",
                "strict": True,
                "description": "更新分析脚本。必须传入脚本 ID script_id 和脚本内容 script。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "script_id": {
                            "type": "string",
                            "description": "要更新的脚本 ID。"
                        },
                        "script": {
                            "type": "string",
                            "description": "要更新的脚本内容。"
                        }
                    },
                    "required": ["script_id", "script"],
                    "additionalProperties": False
                }
            }
        }

    )

    tool_manager.register(
        name="update_analysis_script_from",
        func=update_analysis_script_from,
        schema={
            "type": "function",
            "function": {
                "name": "update_analysis_script_from",
                "strict": True,
                "description": "从表单内容更新分析脚本。必须传入脚本 ID script_id 和表单内容 content。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "script_id": {
                            "type": "string",
                            "description": "要更新的脚本 ID。"
                        },
                        "content": {
                            "type": "string",
                            "description": "表单内容 JSON 字符串，用于更新脚本。"
                        }
                    },
                    "required": ["script_id", "content"],
                    "additionalProperties": False
                }
            }
        }
    )

    tool_manager.register(
        name="add_example",
        func=add_example,
        schema={
            "type": "function",
            "function": {
                "name": "add_example",
                "strict": True,
                "description": "根据script和form json 为tools 生成测试数据。必须传入 content 参数，内容为示例数据为tsv格式文本。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "tsv格式示例数据文本内容。"
                        }
                    },
                    "required": ["content"],
                    "additionalProperties": False
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
                "strict": True,
                "description": "向前端发出 UI 操作指令，例如跳转页面、更新表单、加载表格等。所有 UI 操作必须通过本工具调用。",
                "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                    "type": "string",
                    "enum": [
                        "ui.show_message",
                        "ui.show_notification",
                        "component.invoke",
                        "router.go",
                        "form.set_value",
                        "form.reset"
                    ],
                    "description": "要执行的 UI 操作类型。"
                    },
                    "payload": {
                    "type": "object",
                    "description": "根据 action 不同而变化的参数对象。",
                    "properties": {
                        "type": { "type": "string", "description": "ui.show_message/ui.show_notification 使用：消息类型 success|error|info|warning" },
                        "text": { "type": "string", "description": "ui.show_message 使用：提示文本" },
                        "message": { "type": "string", "description": "ui.show_notification 使用：消息标题" },
                        "description": { "type": "string", "description": "ui.show_notification 使用：消息详情" },
                        "category": { "type": "string", "description": "component.invoke 使用：组件分类" },
                        "id": { "type": "string", "description": "component.invoke 使用：组件 ID" },
                        "method": { "type": "string", "description": "component.invoke 使用：调用方法名" },
                        "args": { "type": "array", "description": "component.invoke 使用：方法参数列表" },
                        "path": { "type": "string", "description": "router.go 使用：跳转路径" },
                        "state": { "description": "router.go 使用：路由状态" },
                        "form": { "type": "string", "description": "form.set_value/form.reset 使用：表单名" },
                        "field": { "type": "string", "description": "form.set_value 使用：字段名" },
                        "value": { "description": "form.set_value 使用：字段值" }
                    },
                    "additionalProperties": True
                    },
                    "actions": {
                    "type": "array",
                    "description": "可选。批量 UI 操作，按顺序执行。用于一次指令包含多个动作（例如先路由跳转再跳到表格最后一页）。",
                    "items": {
                        "type": "object",
                        "properties": {
                        "action": {
                            "type": "string",
                            "enum": [
                            "ui.show_message",
                            "ui.show_notification",
                            "component.invoke",
                            "router.go",
                            "form.set_value",
                            "form.reset"
                            ]
                        },
                        "payload": {
                            "type": "object",
                            "additionalProperties": True
                        }
                        },
                        "required": ["action", "payload"],
                        "additionalProperties": False
                    }
                    }
                },
                "additionalProperties": False,
                "anyOf": [
                    {"required": ["action", "payload"]},
                    {"required": ["actions"]}
                ]
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
