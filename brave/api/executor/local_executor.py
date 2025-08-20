import json
import os
import asyncio
import psutil
import signal
import subprocess
import threading
from pathlib import Path
from typing import Dict

from brave.api.core.evenet_bus import EventBus
from brave.api.executor.base import JobExecutor
from brave.api.executor.models import JobSpec
from brave.api.config.config import Settings, get_settings
from brave.api.core.routers_name import RoutersName
from brave.api.core.event import AnalysisExecutorEvent
from brave.api.schemas.analysis import AnalysisId
# PROCESS_FILE = Path("/tmp/local_processes.json")  # 可配置

class LocalExecutor(JobExecutor):
    def __init__(self,event_bus:EventBus):
        self.event_bus = event_bus
        self.settings:Settings = get_settings()
        self.PROCESS_FILE = self._process_file()
        self.loop = asyncio.get_event_loop()

        self._processes: Dict[str, int] = {}
        self._load_processes()
   
    def _process_file(self):
        return f"{self.settings.BASE_DIR}/local_processes.json"

    def _save_processes(self):
        try:
            with open(self.PROCESS_FILE, "w") as f:
                json.dump(self._processes, f)
        except Exception as e:
            print(f"[LocalExecutor] Failed to persist process map: {e}")

    def _load_processes(self):
        if Path(self.PROCESS_FILE).exists():
            try:
                with open(self.PROCESS_FILE, "r") as f:
                    data = json.load(f)
                    for job_id, pid in data.items():
                        try:
                            proc = psutil.Process(pid)
                            if proc.is_running():
                                self._processes[job_id] = pid
                                # 重启后的 wait 监听
                                threading.Thread(
                                    target=self._wait_and_cleanup_factory(pid, job_id),
                                    daemon=True
                                ).start()
                        except Exception:
                            continue  # 跳过无效进程
            except Exception as e:
                print(f"[LocalExecutor] Failed to load persisted processes: {e}")

    def _wait_and_cleanup_factory(self, pid: int, job_id: str):
        def _wait():
            try:
                psutil.Process(pid).wait()
            except Exception:
                pass
            self._processes.pop(job_id, None)
            self._save_processes()
            analysis_id = AnalysisId(analysis_id=job_id)
            asyncio.run_coroutine_threadsafe(self.event_bus.dispatch(RoutersName.ANALYSIS_EXECUTER_ROUTER,AnalysisExecutorEvent.ON_ANALYSIS_COMPLETE,analysis_id),self.loop)
            print(f"[JobManager] Process {job_id} with PID {pid} exited and cleaned.")
        return _wait

    async def _do_submit_job(self, job_spec) -> str:
        if job_spec.job_id in self._processes:
            pid = self._processes[job_spec.job_id]
            try:
                proc = psutil.Process(pid)
                if proc.is_running():
                    raise Exception(f"Analysis already running with PID={pid}")
            except psutil.NoSuchProcess:
                pass  # 继续重新提交

        proc = subprocess.Popen(
            job_spec.command,
            cwd=job_spec.output_dir,
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        self._processes[job_spec.job_id] = proc.pid
        self._save_processes()

        threading.Thread(
            target=self._wait_and_cleanup_factory(proc.pid, job_spec.job_id),
            daemon=True
        ).start()

        return str(proc.pid)

    def stop_job(self, job_id: str) -> None:
        pid = self._processes.get(job_id)
        if pid:
            try:
                proc = psutil.Process(pid)
                if proc.is_running():
                    os.killpg(pid, signal.SIGTERM)
                    print(f"[JobManager] Terminated process group of PID {pid}")
                else:
                    raise Exception(f"Process {pid} not running")
            finally:
                self._processes.pop(job_id, None)
                self._save_processes()

    def get_logs(self, job_id: str) -> str:  
        return super().get_logs(job_id)