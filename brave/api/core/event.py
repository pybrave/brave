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
    ON_ANALYSIS_SUBMITTED="on_analysis_submitted"
    ON_ANALYSIS_COMPLETE="on_analysis_complete"
    ON_CONTAINER_PULLED = "on_container_pulled"
    ON_ANALYSIS_FAILED="on_analysis_failed"
    ON_ANALYSIS_STARTED="on_analysis_started"
    ON_ANALYSIS_STOPED="on_analysis_stoped"

class AnalysisResultEvent(str,Enum):
    ON_ANALYSIS_RESULT_ADD="on_analysis_result_add"
    ON_ANALYSIS_RESULT_UPDATE="on_analysis_result_update"
    ON_ANALYSIS_RESULT_DELETE="on_analysis_result_delete"
    ON_ANALYSIS_RESULT_QUERY="on_analysis_result_query"
    ON_ANALYSIS_RESULT_QUERY_BY_ID="on_analysis_result_query_by_id"
    ON_ANALYSIS_RESULT_QUERY_BY_ANALYSIS_ID="on_analysis_result_query_by_analysis_id"
    ON_ANALYSIS_RESULT_QUERY_BY_COMPONENT_ID="on_analysis_result_query_by_component_id"
    ON_ANALYSIS_RESULT_QUERY_BY_SAMPLE_ID="on_analysis_result_query_by_sample_id"