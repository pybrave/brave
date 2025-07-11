import asyncio
import inspect
from importlib import import_module
from importlib.resources import files
from functools import lru_cache
class ListenerFilesService:
    def __init__(self):
        self.listener_files = self._load_listener_files()

    def _load_listener_files(self):
        """
        加载监听器文件列表
        """
        listener_files = files("brave.api.listener")
        return [
            item.stem
            for item in listener_files.iterdir()
            if item.is_file() and item.name.endswith(".py") and item.name != "__init__.py" and item.name.startswith("file")
        ]

    async def execute_listener(self, func, args):
        """
        执行监听器的回调函数
        """
        if isinstance(self.listener_files, list) and len(self.listener_files) > 0:
            for name in self.listener_files:
                full_module = f"brave.api.listener.{name}"
                mod = import_module(full_module)
                if hasattr(mod, func):
                    run_func = getattr(mod, func)
                    if inspect.iscoroutinefunction(run_func):
                        asyncio.create_task(run_func(**args))
                    else:
                        await asyncio.to_thread(run_func, **args)

    def get_listener_files(self):
        return self.listener_files
    
    def add_listener_file(self,listener_file):
        self.listener_files.append(listener_file)
    
    def remove_listener_file(self,listener_file):
        self.listener_files.remove(listener_file)

@lru_cache()
def get_listener_files_service():
    return ListenerFilesService()