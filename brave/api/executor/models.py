# models.py
from typing import List,Optional
from pydantic import BaseModel
import hashlib
import json
           
class JobSpec(BaseModel):
    job_id: str
    command: List[str]
    output_dir: str
    command_log_path: str
    # image: str = ""
    # env: dict = {}
    # resources: dict = {}

    # def fingerprint(self) -> str:
    #     key = {
    #         "cmd": self.command,
    #         "img": self.image,
    #         "env": self.env,
    #         "res": self.resources,
    #     }
    #     return hashlib.sha256(json.dumps(key, sort_keys=True).encode()).hexdigest()
class LocalJobSpec(JobSpec):
    process_id: Optional[int]=None


class DockerJobSpec(JobSpec):
    container_id: str
    resources: dict
    run_type:str
    change_uid:bool


class JobStatus(BaseModel):
    job_id: str
    state: str
    detail: str = ""
