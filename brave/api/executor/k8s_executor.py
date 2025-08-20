# container/k8s_backend.py
from kubernetes import client, config
from brave.api.executor.models import JobSpec
from brave.api.core.evenet_bus import EventBus
from .base import JobExecutor   
from brave.api.core.routers.workflow_event_router import WorkflowEventRouter
class K8sExecutor(JobExecutor):
    def __init__(self,event_bus:EventBus):
        self.event_bus = event_bus
        config.load_kube_config()
        self.api = client.CoreV1Api()
        self.batch_api = client.BatchV1Api()

    async def _do_submit_job(self, job_spec) -> str:
        # 这里应构造 Job YAML spec
        job = client.V1Job(...)  # 构建 Job 对象
        self.batch_api.create_namespaced_job(namespace="default", body=job)
        return job.metadata.name

    def get_logs(self, job_id: str) -> str:
        pod_list = self.api.list_namespaced_pod("default", label_selector=f"job-name={job_id}")
        pod_name = pod_list.items[0].metadata.name
        return self.api.read_namespaced_pod_log(pod_name, namespace="default")

    def stop_job(self, job_id: str) -> None:
        self.batch_api.delete_namespaced_job(name=job_id, namespace="default", propagation_policy='Foreground')
