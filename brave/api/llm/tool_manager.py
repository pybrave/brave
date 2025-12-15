# tool_manager.py
import json
import asyncio

class ToolManager:
    def __init__(self):
        self.tools = {}

    def register(self, name: str, func, description: str = "", parameters: dict = None):
        # self.tools[name] = [
        #         {
        #             "type": "function",
        #             "function": {
        #                 "name": name,
        #                 "description": description,
        #                 "parameters": parameters or {"type": "object", "properties": {}},
        #             }
        #         }
        #     ]
        self.tools[name] = {
            "func": func,
            "schema": {
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": parameters or {"type": "object", "properties": {}},
                },
            },
        }

    def get_schemas(self):
        """ 给 DeepSeek 的 tools 参数 """
        return [tool["schema"] for tool in self.tools.values()]

    async def run(self, name: str, arguments: dict):
        """真正执行工具"""
        tool = self.tools.get(name)
        if not tool:
            return f"[Tool Error] Tool '{name}' not registered."

        func = tool["func"]
        if asyncio.iscoroutinefunction(func):
            if "parameters" in arguments:
                arguments = {**arguments["parameters"], **arguments}
                del arguments["parameters"]
            return await func(arguments)
        return func(**arguments)
