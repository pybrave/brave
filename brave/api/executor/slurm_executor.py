# container/slurm_backend.py
import subprocess

from brave.api.executor.models import JobSpec
from .base import JobExecutor
from brave.api.core.evenet_bus import EventBus  
class SlurmExecutor(JobExecutor):
    def __init__(self,event_bus:EventBus):
        self.event_bus = event_bus
    async def _do_submit_job(self, job_spec):
        pass
        # script_path = job_spec["script_path"]
        # result = subprocess.run(["sbatch", script_path], capture_output=True, text=True)
        # job_id = result.stdout.strip().split()[-1]
        # return job_id

    def get_logs(self, job_id: str) -> str:
        log_path = f"/path/to/logs/{job_id}.out"
        with open(log_path) as f:
            return f.read()

    def stop_job(self, job_id: str) -> None:
        subprocess.run(["scancel", job_id])
