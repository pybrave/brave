from ast import Dict, Set
import asyncio
import psutil
from watchfiles import awatch
from datetime import datetime
from brave.api.config.db import get_engine
from brave.api.models.core import analysis
from sqlalchemy import select, update
import logging
from importlib.resources import files
from importlib import import_module
import inspect
from brave.api.service.sse_service import SSESessionService
from brave.api.service.analysis_result_parse import AnalysisResultParse
from collections import defaultdict
from typing import Dict, Set
from brave.api.service.listener_files_service import ListenerFilesService
# 创建 logger
logger = logging.getLogger(__name__)

class ProcessMonitor:
    def __init__(self, 
    sse_service: SSESessionService,
    analysis_result_parse_service: AnalysisResultParse,
    listener_files_service: ListenerFilesService,
    check_interval: int = 5,
     
    ):
        self.queue_process = asyncio.Queue()
        self.queue_lock = asyncio.Lock()  # 保证数据库更新和队列操作安全
        self.check_interval = check_interval  # 检查间隔
        # self.listener_files = self._load_listener_files()
        self.sse_service = sse_service
        self.analysis_id_to_queue: Dict[str, Set[asyncio.Queue]] = defaultdict(set)
        self.analysis_result_parse_service = analysis_result_parse_service
        self.listener_files_service = listener_files_service
    # def _load_listener_files(self):
    #     """
    #     加载监听器文件列表
    #     """
    #     listener_files = files("brave.api.listener")
    #     return [
    #         item.stem
    #         for item in listener_files.iterdir()
    #         if item.is_file() and item.name.endswith(".py") and item.name != "__init__.py" and item.name.startswith("file")
    #     ]

    # async def execute_listener(self, func, args):
    #     """
    #     执行监听器的回调函数
    #     """
    #     if isinstance(self.listener_files, list) and len(self.listener_files) > 0:
    #         for name in self.listener_files:
    #             full_module = f"brave.api.listener.{name}"
    #             mod = import_module(full_module)
    #             if hasattr(mod, func):
    #                 run_func = getattr(mod, func)
    #                 if inspect.iscoroutinefunction(run_func):
    #                     asyncio.create_task(run_func(**args))
    #                 else:
    #                     await asyncio.to_thread(run_func, **args)

    async def startup_process_event(self):
        """
        初始化队列中的任务，加载数据库中的数据到队列中
        """
        with get_engine().begin() as conn:
            stmt = select(analysis).where(analysis.c.process_id != None)
            results = conn.execute(stmt).all()
            for row in results:
                item = dict(row._mapping)
                await self.queue_process.put(item)

        logger.info(f"队列初始化完毕，任务数：{self.queue_process.qsize()}")
        # 启动进程检查工作
        # asyncio.create_task()
        await self.check_process_worker()

    async def check_process_worker(self):
        """
        负责检查进程是否存在，每隔一段时间重新检查队列中的任务
        """
        while True:
            item = await self.queue_process.get()
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
                await self.clean_up_process(item)
            else:
                # 进程存在且符合要求，延迟后重新入队
                await asyncio.sleep(self.check_interval)
                await self.queue_process.put(item)
            finally:
                self.queue_process.task_done()

    async def clean_up_process(self, item):
        """
        清理数据库中的 process_id 字段，并触发监听器事件
        """
        analysis_id = item.get("analysis_id")
        # 确保数据库操作的线程安全
        async with self.queue_lock:
            await self.listener_files_service.execute_listener("process_end", {
                "analysis": item,
                "sse_service": self.sse_service,
                "analysis_result_parse_service":self.analysis_result_parse_service})

    async def add_process(self, analysis_dict):
        async with self.queue_lock:
            await self.queue_process.put(analysis_dict)

    async def get_process(self):
        return await self.queue_process.get()