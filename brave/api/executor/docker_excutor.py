import asyncio
from concurrent.futures import ThreadPoolExecutor
import os
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
from docker.errors import NotFound, APIError
import traceback
import brave.api.service.container_service as container_service
from brave.api.config.db import get_engine
import json
from brave.api.schemas.analysis import AnalysisExecuterModal
from docker.errors import ImageNotFound
from brave.api.service import container_service
import os

from brave.api.service import namespace_service


class DockerExecutor(JobExecutor):

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.client = docker.from_env()
        self.containers: Dict[str, Container] = {}
        # self._monitor_task = None
        self._monitor_interval = 2.0  # 秒
        self.to_remove = []
        self.setting  = get_settings()
        asyncio.create_task(self.recover_running_containers())
        asyncio.create_task(self._monitor_containers())
        asyncio.create_task(self.update_images_status())
        self.running_conntainer =  []
        asyncio.create_task(asyncio.to_thread(self._list_running))
        self.executor = ThreadPoolExecutor(max_workers=5)
        


    async def recover_running_containers(self):
        """
        程序启动时调用：
        从数据库查询所有运行中分析，恢复对应容器监控
        """
        with get_engine().begin() as conn:  
            running_jobs = find_running_analysis(conn)  # 异步获取所有运行中任务

        for job in running_jobs:
            try:
                # containers = self.client.containers.list(
                #     all=True,
                #     filters={"label": f"run_type=job"}
                # )

                # # 找到匹配的容器
                # container = next(
                #     (c for c in containers if c.name == job.analysis_id),
                #     None
                # )
                # if container:
                #     container = self.client.containers.get(job.analysis_id)
                #     self.containers[job.analysis_id] = container
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
    async def _do_submit_job(self, job: AnalysisExecuterModal) :
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
    def is_already_running(self, job_id: str) -> bool:
        try:
            self.client.containers.get(job_id)
            return True
        except NotFound:
            return False



#  job_id= payload.analysis_id,
#                 command_log_path= payload.command_log_path,
#                 command=["./run.sh"],
#                 output_dir= payload.output_dir,
#                 container_id=payload.container_id,
#                 run_type=payload.run_type,
#                 change_uid=
#                 resources={}
    def _sync_submit_job(self, job: AnalysisExecuterModal) -> str:
        user_id = os.getuid() 
        group_id = os.getgid()

        with get_engine().begin() as conn: 
            find_container = container_service.find_container_by_id(conn,job.container_id)
            # find_namespace = namespace_service.find_namespace(conn,job.namespace)
            if not find_container:
                raise RuntimeError(f"Container {job.container_id} not found")
            # if not find_namespace:
            #     raise RuntimeError(f"Namespace {job.namespace} not found")
        # {
        # "DISABLE_AUTH":true,
        # "USERID":"$USERID",
        # "GROUPID":"$GROUPID",
        # "R_USER_WORKDIR":"$OUTPUT_DIR",
        # "R_SCRIPT":"$SCRIPT_FILE"
        # }
        sock_gid = os.stat('/var/run/docker.sock').st_gid
        settings = get_settings()
        work_dir = str(settings.WORK_DIR)
        pipeline_dir = str(settings.PIPELINE_DIR)
        base_dir = str(settings.BASE_DIR)
        script_dir = os.path.dirname(job.pipeline_script)
        connom_script_dir = os.path.dirname(script_dir)
        envionment = {}
        if find_container["envionment"]:
            envionment = find_container["envionment"]
            envionment = envionment.replace("$USERID", str(user_id))
            envionment = envionment.replace("$GROUPID", str(group_id))
            envionment = envionment.replace("$DOCKER_GROUPID", str(sock_gid))

            envionment = envionment.replace("$SCRIPT_DIR", script_dir)
            envionment = envionment.replace("$OUTPUT_DIR", job.output_dir)
            envionment = envionment.replace("$SCRIPT_FILE", job.pipeline_script)
            envionment = json.loads(envionment) 
    
        # command = job.command
        # command.extend  (["2>&1","|","tee",f"{job.output_dir}/run.log"])
        # try:
        #     self.client.containers.get(job.job_id)
        #     raise RuntimeError(f"Container {job.job_id} already exists")
        # except NotFound:
        #     pass  # 容器不存在，正常流程
        # except Exception as e:
        #     print(f"Error checking container existence: {e}")
        #     self.to_remove.append(job.job_id)
        #     raise e  # 其他错误不应吞掉



        command = f"-c  \"bash ./run.sh  2>&1 | tee {job.command_log_path}; exit ${{PIPESTATUS[0]}}\""
        port = {}
        docker_uid = user_id
        labels ={}
        network = None
        url_predix = f"container/{job.analysis_id}"
        if job.run_type=="server" or job.run_type=="retry":
            command = find_container["command"] or  ""
            command = command.replace("$SCRIPT_DIR",script_dir)
            command = command.replace("$URL_PREFIX",url_predix)
            # command = f"{command}  > {job.command_log_path}"
            port = {}
            port_str = find_container["port"]
            if ":" in port_str:
                for item in port_str.split(","):
                    host_port, container_port = item.split(":")
                    # Docker SDK 需要字典 {container_port/tcp: host_port}
                    port[f"{container_port}/tcp"] = int(host_port)
            elif  port!="":
                port =  {f"{port_str}/tcp":None}

            docker_uid = user_id if find_container["change_uid"] else None
            labels = find_container["labels"]
            if labels:
                labels = labels.replace("$URL_PREFIX",url_predix)
                labels = labels.replace("$CONTAINER_NAME",job.analysis_id)
                labels = json.loads(labels)
            else:
                labels={}
            
            try:
                network = self.client.networks.get("traefik_proxy")
            except docker.errors.NotFound:
                network = self.client.networks.create("traefik_proxy", driver="bridge")
            network = "traefik_proxy"
            # $SCRIPT_DIR
        volumes = {}

        if find_container.volumes:
            volumes_dict = json.loads(find_container.volumes)
            for k,v in volumes_dict.items():
                if os.path.exists(k):
                    volumes.update({ k: v})

        # if os.path.exists("/data"):
        #     volumes.update({ "/data": {
        #                 "bind": "/data",
        #                 "mode": "rw"
        #             }})
        entrypoint = None
        if  job.run_type=="job":
            entrypoint="bash"
        try:
            container: Container = self.client.containers.run(
                image=find_container.image,
                name=job.analysis_id,
                user= docker_uid,
                group_add=["users",str(sock_gid)],
                command=command,
                network=network,
                entrypoint=entrypoint,
                volumes={
                    job.output_dir: {
                        "bind": job.output_dir,
                        "mode": "rw"
                    },
                    script_dir:{
                        "bind": script_dir,
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
                    **volumes,
                    "/usr/bin/docker":{
                        "bind": "/usr/bin/docker",
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
                environment={
                    **envionment,
                    "PIPELINE_DIR": f"{pipeline_dir}",
                    "OUTPUT_DIR":f"{job.output_dir}",
                    "COMMON_SCRIPT_DIR":f"{connom_script_dir}/common"
                },
                working_dir=job.output_dir,
                detach=True,
                labels={
                    "job_id": job.analysis_id,
                    "project": "brave",
                    "user": str(user_id),
                    "run_type":job.run_type,
                    **labels
                },
                 ports=port
                # remove=True
            )
            
        except Exception as e:
            print(f"Error running container {job.analysis_id}: {e}")
            self.to_remove.append(job.analysis_id)
            raise e
        if container.id is None:
            raise RuntimeError("Container did not return a valid ID")
        
        self.containers[job.analysis_id] = container
        container.reload()
        ports = container.attrs['NetworkSettings']['Ports']
        job.ports = ports
        # if self._monitor_task is None:
        #     self._monitor_task = asyncio.create_task(self._monitor_containers())
        self._list_running()
        asyncio.run(self.event_bus.dispatch(
            RoutersName.ANALYSIS_EXECUTER_ROUTER,
            AnalysisExecutorEvent.ON_ANALYSIS_STARTED,
            job
        ) )  
        return container.id



    async def _monitor_containers(self):
        while True:
            try:
                for job_id, container in list(self.containers.items()):
                    try:
                        container.reload()
                        analysis_id = AnalysisId(analysis_id=job_id)
                        if container.status in ("exited", "dead"):
                            exit_code = container.attrs["State"]["ExitCode"]

                            if exit_code == 0:
                                # 成功退出，自动删除容器
                                print(f"[{job_id}] 执行成功，删除容器")
                                container.remove(force=True)
                                self.containers.pop(job_id, None)
                                
                                await self.event_bus.dispatch(
                                    RoutersName.ANALYSIS_EXECUTER_ROUTER,
                                    AnalysisExecutorEvent.ON_ANALYSIS_COMPLETE,
                                    analysis_id
                                )
                                self._list_running()
                            else:
                                # 执行失败，保留容器调试
                                print(f"[{job_id}] 执行失败（ExitCode={exit_code}），保留容器")
                                self.containers.pop(job_id, None)  # 不删除容器，仅移出监控
                                await self.event_bus.dispatch(
                                    RoutersName.ANALYSIS_EXECUTER_ROUTER,
                                    AnalysisExecutorEvent.ON_ANALYSIS_FAILED,
                                    analysis_id
                                )  
                                self._list_running()
                    except Exception as e:
                        print(f"Error monitoring container {job_id}: {e}")
                        self.to_remove.append(job_id)
                        self._list_running()
                

                for job_id in self.to_remove:
                    if job_id in self.containers:
                        self.containers.pop(job_id, None)
                    analysis_id = AnalysisId(analysis_id=job_id)
                    await self.event_bus.dispatch(
                            RoutersName.ANALYSIS_EXECUTER_ROUTER,
                            AnalysisExecutorEvent.ON_ANALYSIS_COMPLETE,
                            analysis_id
                        )
                    self.to_remove.remove(job_id)
                await asyncio.sleep(self._monitor_interval)
            except Exception as e:
            
                print(f"Error auto removing container {job_id}: {e}")
                traceback.print_exc()
                pass

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
            self._list_running()
        except Exception as e:
            print(f"Error stopping container {job_id}: {e}")
            pass
    
    async def remove_job(self, job_id: str) -> None:
        try:
            self.client.containers.get(job_id).remove(force=True)
            self._list_running()
        except Exception as e:
            print(f"Error removing container {job_id}: {e}")
            pass

    def _list_running(self) :
        label_filter = {"label": "project=brave"}
        # 获取运行中的容器（filtered by label）
        containers = self.client.containers.list(filters=label_filter)
        containers = [{container.name:container.id} for container in containers]
        self.running_conntainer = containers
    
    async def list_running(self) :
        return self.running_conntainer

    async def update_images_status(self):
        with get_engine().begin() as conn: 
            container_list = container_service.list_container(conn)
            for item in container_list:
                image = self.get_image(item.image)
                if image:
                    container_service.update_container(conn,
                                                       item.container_id,
                                                       {"image_id":image.id,"image_status":"exist"})
                else:
                    container_service.update_container(conn,
                                                       item.container_id,
                                                       {"image_status":"not_exist"})
             
            

    def get_image(self, image_name):
        try:
            image = self.client.images.get(image_name)
            return image
        except ImageNotFound:
            print(f"Image ({image_name}) not exist!")
            return None
        except Exception as e:
            return None
    
    def pull_image_with_log(self,container_id,image_name: str):
        client = docker.APIClient(base_url="unix://var/run/docker.sock")
        stream = client.pull(image_name.strip(), stream=True, decode=True)
        log_file = f"{self.setting.BASE_DIR}/log"
        if not  os.path.exists(log_file):    
            os.makedirs(log_file) 
        print(f"pull {image_name} log :{log_file}/{container_id}.log")
        with open(f"{log_file}/{container_id}.log", "w", encoding="utf-8") as f:
            for log in stream:
                log_str = json.dumps(log, ensure_ascii=False)
                # print(log_str)  # 继续打印到控制台
                f.write(log_str + "\n")  # 写入文件

        # for log in stream:
            
        #     print(json.dumps(log, indent=2, ensure_ascii=False))

    async def pull_image(self,container_id,image_name):
        print(f"pull {image_name}")
        # a = self.client.images.pull(image_name)
        
        await asyncio.to_thread(self.pull_image_with_log,container_id,image_name)
        image = self.get_image(image_name)
        if image:
            print(f"pull {image_name} complete!")
            with get_engine().begin() as conn: 
                container_service.update_container(conn,
                                                    container_id,
                                                    {"image_id":image.id,"image_status":"exist"})
        analysis_id = AnalysisId(analysis_id=container_id)
        # asyncio.create_task() 
        await self.event_bus.dispatch(
            RoutersName.ANALYSIS_EXECUTER_ROUTER,
            AnalysisExecutorEvent.ON_CONTAINER_PULLED,
            analysis_id
        )
    async def get_container_attr(self,container_id):
        try:
            container = self.client.containers.get(container_id)
            container.reload()
            return container.attrs
        except Exception as e:
            print(f"Error getting attrs for container {container_id}: {e}")
            return None
    async def get_image_attr(self,image_name):
        try:
            image = self.client.images.get(image_name)
            return image.attrs
        except Exception as e:
            print(f"Error getting attrs for image {image_name}: {e}")
            return None