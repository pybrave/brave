from abc import ABC, abstractmethod
from brave.api.executor.models import JobSpec
class JobExecutor(ABC):

    @abstractmethod
    def submit_job(self, job_spec: JobSpec) -> str:
        pass

    @abstractmethod
    def get_logs(self, job_id: str) -> str:
        pass

    @abstractmethod
    def stop_job(self, job_id: str) -> None:
        pass
