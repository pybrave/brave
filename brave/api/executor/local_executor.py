# container/slurm_backend.py
import subprocess
from brave.api.executor.models import LocalJobSpec
from .base import JobExecutor
import threading
import psutil

class LocalExecutor(JobExecutor):
    def submit_job(self, job_spec: LocalJobSpec) -> str:

        try:
            if job_spec.process_id is not None:
                proc = psutil.Process(int(job_spec.process_id))
                if proc.is_running():
                    raise Exception(f"Analysis is already running with process_id={job_spec.process_id}")
        except (psutil.NoSuchProcess, ValueError):
            pass  
        proc = subprocess.Popen(
            job_spec.command,
            cwd=job_spec.output_dir, 
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        threading.Thread(target=proc.wait, daemon=True).start() # 处理僵尸进程
        return str(proc.pid)

    def get_logs(self, job_id: str) -> str:
        log_path = f"/path/to/logs/{job_id}.out"
        with open(log_path) as f:
            return f.read()

    def stop_job(self, job_id: str) -> None:
        subprocess.run(["scancel", job_id])


