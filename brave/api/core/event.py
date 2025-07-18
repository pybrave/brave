from enum import Enum


class IngressEvent(str, Enum):
    NEXTFLOW_EXECUTOR_EVENT = "nextflow_executor_event"
    HEARTBEAT = "__heartbeat__"

class WatchFileEvent(str,Enum):
    WORKFLOW_LOG ="workflow_log"
    TRACE_LOG="trace_log"

class WorkflowEvent(str,Enum):
    ON_FLOW_BEGIN="on_flow_begin"
    ON_PROCESS_COMPLETE="on_process_complete"
    ON_FLOW_COMPLETE="on_flow_complete"
    ON_JOB_SUBMITTED="on_job_submitted"
    ON_FILE_PUBLISH="on_file_publish"
    WORKFLOW_CLEANUP="workflow_cleanup"

class AnalysisExecutorEvent(str,Enum):
    ON_ANALYSIS_COMPLETE="on_analysis_complete"