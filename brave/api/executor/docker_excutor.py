import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict
import docker
from docker.models.containers import Container
from brave.api.core.evenet_bus import EventBus
from brave.api.core.event import AnalysisExecutorEvent
from brave.api.core.routers_name import RoutersName
from brave.api.executor.models import DockerJobSpec
from brave.api.schemas.analysis import AnalysisId
from brave.api.service.analysis_service import find_running_analysis
from .base import JobExecutor
from brave.api.core.routers.workflow_event_router import WorkflowEventRouter    
from brave.api.config.config import get_settings
from brave.api.config.db import get_engine


class DockerExecutor(JobExecutor):

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.client = docker.from_env()
        self.containers: Dict[str, Container] = {}
        # self._monitor_task = None
        self._monitor_interval = 2.0  # 秒
        self.to_remove = []
        asyncio.create_task(self.recover_running_containers())
        asyncio.create_task(self._monitor_containers())
        self.executor = ThreadPoolExecutor(max_workers=5)
        
    async def _do_submit_job(self, job: DockerJobSpec) :
        # loop = asyncio.get_running_loop()
        # await loop.run_in_executor(
        #     self.executor,
        #     self._sync_submit_job,
        #     job
        # )
        asyncio.create_task(asyncio.to_thread(self._sync_submit_job, job))

        # await asyncio.to_thread(self._sync_submit_job,job)
        pass
        # return container_id

    async def recover_running_containers(self):
        """
        程序启动时调用：
        从数据库查询所有运行中分析，恢复对应容器监控
        """
        with get_engine().begin() as conn:  
            running_jobs = find_running_analysis(conn)  # 异步获取所有运行中任务

        for job in running_jobs:
            try:
                container = self.client.containers.get(job.analysis_id)
                self.containers[job.analysis_id] = container
            except Exception as e:
                print(f"Error recovering container {job.analysis_id}: {e}")
                # 容器不存在，可能已退出或删除
                # await self.event_bus.dispatch(
                #     RoutersName.ANALYSIS_EXECUTER_ROUTER,
                #     AnalysisExecutorEvent.ON_ANALYSIS_COMPLETE,
                #     AnalysisId(analysis_id=job.analysis_id)
                # )
                self.to_remove.append(job.analysis_id)
                pass

        # if self.containers and self._monitor_task is None:
        # self._monitor_task = asyncio.create_task(self._monitor_containers())

    def _sync_submit_job(self, job: DockerJobSpec) -> str:
        settings = get_settings()
        work_dir = str(settings.WORK_DIR)
        pipeline_dir = str(settings.PIPELINE_DIR)
        base_dir = str(settings.BASE_DIR)

        container: Container = self.client.containers.run(
            image=job.image,
            name=job.job_id,
            command=job.command,
            volumes={
                job.output_dir: {
                    "bind": job.output_dir,
                    "mode": "rw"
                },
                work_dir: {
                    "bind": work_dir,
                    "mode": "rw"
                },
                pipeline_dir: {
                    "bind": pipeline_dir,
                    "mode": "rw"
                },
                base_dir: {
                    "bind": base_dir,
                    "mode": "rw"
                },
                "/tmp/brave.sock": {
                    "bind": "/tmp/brave.sock",
                    "mode": "rw"
                },
                "/var/run/docker.sock": {
                    "bind": "/var/run/docker.sock",
                    "mode": "rw"
                }
            },
            environment=job.env,
            working_dir=job.output_dir,
            detach=True,
            remove=True
        )
        if container.id is None:
            raise RuntimeError("Container did not return a valid ID")

        self.containers[job.job_id] = container

        # if self._monitor_task is None:
        #     self._monitor_task = asyncio.create_task(self._monitor_containers())

        return container.id

    async def _monitor_containers(self):
        while True:
            
            for job_id, container in self.containers.items():
                try:
                    container.reload()
                    if container.status == "exited" or container.status == "dead":
                        self.to_remove.append(job_id)
                except Exception as e:
                    print(f"Error monitoring container {job_id}: {e}")
                    self.to_remove.append(job_id)

            for job_id in self.to_remove:
                self.containers.pop(job_id, None)
                analysis_id = AnalysisId(analysis_id=job_id)
                await self.event_bus.dispatch(
                        RoutersName.ANALYSIS_EXECUTER_ROUTER,
                        AnalysisExecutorEvent.ON_ANALYSIS_COMPLETE,
                        analysis_id
                    )
                self.to_remove.remove(job_id)

            await asyncio.sleep(self._monitor_interval)

    def get_logs(self, job_id: str) -> str:
        try:
            logs = self.client.containers.get(job_id).logs()
            print(f"logs: {logs}")
            if logs is None:
                return ""
            return logs.decode()
        except Exception as e:
            print(f"Error getting logs for container {job_id}: {e}")
            return ""

    def stop_job(self, job_id: str) -> None:
        try:
            self.client.containers.get(job_id).stop()
        except Exception as e:
            print(f"Error stopping container {job_id}: {e}")
            pass
