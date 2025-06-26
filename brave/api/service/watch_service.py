from watchfiles import awatch
from brave.api.routes.sse import global_queue

# 文件变更监控任务
async def watch_folder(path: str):
    async for changes in awatch(path, recursive=False):
        for change, file_path in changes:
            msg = f"{change.name.upper()} {file_path}"
            await global_queue.put(msg)
                