from abc import ABC, abstractmethod
from brave.api.core.event import WorkflowEvent
from brave.api.executor.models import JobSpec
from brave.api.core.routers.workflow_event_router import WorkflowEventRouter
class JobExecutor(ABC):
    def __init__(self):
        pass
    async def submit_job(self, job_spec: JobSpec) -> str:
        if self.is_already_running(job_spec.job_id):
            self.remove_job(job_spec.job_id)
            # raise Exception(f"Job {job_spec.job_id} is already running")
        await self._do_submit_job(job_spec)
        # await self.router.dispatch(WorkflowEvent.ON_JOB_SUBMITTED,{"event": "on_job_submitted", "job_id": job_spec.job_id})
        return job_spec.job_id



    @abstractmethod
    async def _do_submit_job(self, job_spec: JobSpec) -> str:
        pass

    @abstractmethod
    def get_logs(self, job_id: str) -> str:
        pass

    @abstractmethod
    def stop_job(self, job_id: str) -> None:
        pass
    
    def is_already_running(self, job_id: str) -> bool:
        return False 
    
    def remove_job(self, job_id: str) -> None:
        pass