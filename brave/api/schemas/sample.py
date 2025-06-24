from typing import Optional
from pydantic import BaseModel

class ImportSample(BaseModel):
    content: Optional[str]


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

class SampleGroupQuery(BaseModel):
    project: Optional[str]
    sequencing_target: Optional[str]
    sequencing_technique: Optional[str]
    sample_composition: Optional[str]

class SampleGroup(BaseModel):
    id: Optional[int]
    sample_name: Optional[str]
    sample_key: Optional[str]
    sequencing_target: Optional[str]
    sequencing_technique: Optional[str]
    sample_composition: Optional[str]
    sample_group: Optional[str]
    sample_source: Optional[str]
    host_disease: Optional[str]
    project: Optional[str]

class Sample(BaseModel):
    id: Optional[int]
    sample_name: Optional[str]
    sample_key: Optional[str]
    sequencing_target: Optional[str]
    sequencing_technique: Optional[str]
    sample_composition: Optional[str]
    sample_group: Optional[str]
    sample_group_name: Optional[str]
    sample_source: Optional[str]
    host_disease: Optional[str]
    project: Optional[str]
    sample_individual: Optional[str]
    is_available: Optional[int]
    fastq1: Optional[str]
    fastq2: Optional[str]

class ProjectCount(BaseModel):
    project: Optional[str]
    count: Optional[int]