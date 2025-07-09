from watchfiles import awatch
# from brave.api.routes.sse import global_queue
from datetime import datetime
import asyncio
from importlib.resources import files, as_file
from importlib import import_module
from brave.api.config.db import get_engine
from brave.api.models.core import analysis
import psutil
import logging
from sqlalchemy import  select, update
import inspect

# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

listener_files = files("brave.api.listener")
listener_files = [
    item.stem
    for item in listener_files.iterdir() 
    if item.is_file() and item.name.endswith(".py") and item.name != "__init__.py" and item.name.startswith("file")     
]

async def execute_listener(func, args):
    if isinstance(listener_files, list) and len(listener_files) > 0:
        for name in listener_files:
            full_module = f"brave.api.listener.{name}"
            mod = import_module(full_module)
            if hasattr(mod, func):
                run_func = getattr(mod, func)
                if inspect.iscoroutinefunction(run_func):
                    asyncio.create_task(run_func(**args))
                else:
                    await asyncio.to_thread(run_func, **args)


# 文件变更监控任务
async def watch_folder(path: str):
   
    async for changes in awatch(path, recursive=False, step=3000):
        for change, file_path in changes:
            await execute_listener("file_change", {"change":change, "file_path":file_path})
            # msg = f"{change.name.upper()} {file_path}"
            # if len(listener_files) >0:
            #     for name in listener_files:
            #         full_module = f"brave.api.listener.{name}"
            #         mod = import_module(full_module)
            #         if hasattr(mod, "run"):
            #             # await mod.run(change.name.upper(),file_path)
            #             run_func = mod.run
            #             if inspect.iscoroutinefunction(run_func):
            #                 asyncio.create_task(run_func(change.name.upper(), file_path))
            #             else:
            #                 await asyncio.to_thread(run_func, change.name.upper(), file_path)

            # await global_queue.put(msg)


queue_process = asyncio.Queue()
queue_lock = asyncio.Lock()  # 保证数据库更新和队列操作安全

async def startup_process_event():
    with get_engine().begin() as conn:
        stmt = select(analysis).where(analysis.c.process_id != None)
        results = conn.execute(stmt).all()
        for row in results:
            item = dict(row._mapping)
            await queue_process.put(item)
    logger.info(f"队列初始化完毕，任务数：{queue_process.qsize()}")   
    asyncio.create_task(check_process_worker())

CHECK_INTERVAL = 5  # 秒，检查频率
async def check_process_worker():
    while True:
        item = await queue_process.get()
        process_id = item.get("process_id")
        analysis_id = item.get("analysis_id")
        logger.info(f"检查分析任务 id={analysis_id}, pid={process_id}")
        try:
            pid_int = int(process_id)
            proc = psutil.Process(pid_int)
            proc_name = proc.name().lower()
            if "bash" not in proc_name:
                raise psutil.NoSuchProcess(f"进程 {process_id} 不是 nextflow")

        except (psutil.NoSuchProcess, ValueError) as e:
            logger.warning(f"进程 {process_id} 不存在或非 nextflow，清理数据库: {e}")
            # 更新数据库，将 process_id 设为 None
            async with queue_lock:
                with get_engine().begin() as conn:
                    stmt = (
                        update(analysis)
                        .where(analysis.c.analysis_id == analysis_id)
                        .values(process_id=None)
                    )
                    conn.execute(stmt)
                    conn.commit()
                logger.info(f"清理完成 analysis id={analysis_id}")
                await execute_listener("process_end", {"analysis_id":analysis_id})
                # 不重新入队，直接丢弃任务
        else:
            # 进程存在且符合，延迟后重新入队
            await asyncio.sleep(CHECK_INTERVAL)
            await queue_process.put(item)     
        finally:
            queue_process.task_done()





# async def debounce_handler(path, debounce_seconds=2):
#     last_event_time = None
#     debounce_task = None

#     async for changes in awatch(path, recursive=False, step=2000):
#         now = datetime.now()
#         print(f"[{now.strftime('%H:%M:%S')}] 检测到文件变化：{changes}")

#         if debounce_task and not debounce_task.done():
#             debounce_task.cancel()
#             print("取消上一次定时任务")

#         debounce_task = asyncio.create_task(wait_and_handle(debounce_seconds, changes))


# async def wait_and_handle(debounce_seconds, changes):
#     try:
        
#         print(f"✅ {debounce_seconds} 秒后触发处理：{changes}")
#         # 在这里处理变化，比如重新执行某个流程
#         for change, file_path in changes:
#             msg = f"{change.name.upper()} {file_path}"
#             await global_queue.put(msg)

#         await asyncio.sleep(debounce_seconds)

#     except asyncio.CancelledError:
#         # 被新的变化打断
#         pass