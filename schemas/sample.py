from typing import Optional
from pydantic import BaseModel

class Sample(BaseModel):
    id: Optional[int]
    sample_name: Optional[str]
    sequencing_target: Optional[str]
    sequencing_technique: Optional[str]
    sample_composition: Optional[str]
    fastq1: Optional[str]
    fastq2: Optional[str]

class UserCount(BaseModel):
    total: int

