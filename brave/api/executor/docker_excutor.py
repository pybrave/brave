# container/docker_backend.py
import docker
from docker.models.containers import Container

from brave.api.executor.models import DockerJobSpec
from .base import JobExecutor

class DockerExecutor(JobExecutor):
    def __init__(self):
        self.client = docker.from_env()

    def submit_job(self,  job: DockerJobSpec) -> str:
        container: Container = self.client.containers.run(
            image=job.image,
            command=job.command,
            environment=job.env,
            detach=True
        )
        if container.id is None:
            raise RuntimeError("Container did not return a valid ID")
        return container.id

    def get_logs(self, job_id: str) -> str:
        logs = self.client.containers.get(job_id).logs()
        if logs is None:
            return ""
        return logs.decode()

    def stop_job(self, job_id: str) -> None:
        self.client.containers.get(job_id).stop()
