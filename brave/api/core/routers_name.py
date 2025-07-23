from enum import Enum


class RoutersName(str, Enum):
    INGRESS_EVENT_ROUTER = "ingress_event_router"
    WORKFLOW_EVENT_ROUTER = "workflow_event_router"
    WATCHFILE_EVENT_ROUTER = "watchfile_event_router"
    ANALYSIS_EVENT_ROUTER = "analysis_event_router"
    ANALYSIS_EXECUTER_ROUTER = "analysis_executer_router"
    FILE_WATCHER_EVENT_ROUTER = "file_watcher_event_router"
    SSE_EVENT_ROUTER = "sse_event_router"
    HTTP_EVENT_ROUTER = "http_event_router"
    UDS_EVENT_ROUTER = "uds_event_router"
    UDS_STREAM_EVENT_ROUTER = "uds_stream_event_router"
    ANALYSIS_RESULT_ROUTER="analysis_result_router"