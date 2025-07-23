from .docker_excutor import DockerExecutor
from .k8s_executor import K8sExecutor
from .slurm_executor import SlurmExecutor
from .local_executor import LocalExecutor
from .base import JobExecutor
from fastapi import Query
def get_executor(platform: str) -> JobExecutor:
    # workflow_event_router = AppContainer.workflow_event_router()
    if platform == "docker":
        return DockerExecutor()
    elif platform == "k8s":
        return K8sExecutor()
    elif platform == "slurm":
        return SlurmExecutor()
    elif platform == "local":
        return LocalExecutor()
    else:
        raise ValueError(f"Unsupported backend: {platform}")


# def get_executor_dep(
#     platform: str = Query(default="local")  # 可从请求中传入，也支持配置默认值
# ) -> JobExecutor:
#     return get_executor(platform)
