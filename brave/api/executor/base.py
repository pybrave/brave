from abc import ABC, abstractmethod
from brave.api.core.event import WorkflowEvent
from brave.api.executor.models import JobSpec
from brave.api.core.routers.workflow_event_router import WorkflowEventRouter
from brave.api.schemas.analysis import AnalysisExecuterModal

class JobExecutor(ABC):
    def __init__(self):
        pass
    async def submit_job(self, job_spec: AnalysisExecuterModal) -> str:
        if self.is_already_running(job_spec.run_id):
            await self.remove_job(job_spec.run_id)
            # raise Exception(f"Job {job_spec.job_id} is already running")
        await self._do_submit_job(job_spec)
        # await self.router.dispatch(WorkflowEvent.ON_JOB_SUBMITTED,{"event": "on_job_submitted", "job_id": job_spec.job_id})
        return job_spec.analysis_id



    @abstractmethod
    async def _do_submit_job(self, job_spec: AnalysisExecuterModal) -> str:
        pass

    @abstractmethod
    def get_logs(self, job_id: str) -> str:
        pass

    @abstractmethod
    def stop_job(self, job_id: str) -> None:
        pass
    
    def is_already_running(self, job_id: str) -> bool:
        return False 
    
    async def remove_job(self, job_id: str) -> None:
        pass

    async def refresh_list_running(self):
        pass
    def find_running_containers(self,label_filter):
        pass

    async def list_running(self):
        return []

    def get_image(self,image_name):
       pass
    async def pull_image(self,container_id,image_name):
        pass

    async def get_container_attr(self,container_id):
        pass
    async def get_image_attr(self,image_name):
        pass

    async def update_images_status(self):
        pass