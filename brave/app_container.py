# brave/container.py
from dependency_injector import containers, providers
from brave.api.core.routers.workflow_event_router import WorkflowEventRouter
from brave.api.core.workflow_queue import WorkflowQueueManager
from brave.api.core.pubsub import PubSubManager
from brave.api.core.routers.ingress_event_router import IngressEventRouter
from brave.api.ingress.manager import IngressManager
from brave.api.core.workflow_sse import WorkflowSSEManager
from brave.api.service.sse_service import SSESessionService
from brave.api.service.analysis_result_parse import AnalysisResultParse
from brave.api.service.listener_files_service import ListenerFilesService
from brave.api.ingress.factory import IngressMode
from brave.api.core.routers.watch_file_event_router import WatchFileEvenetRouter
from brave.api.core.routers.analysis_executer_router import AnalysisExecutorRouter
class AppContainer(containers.DeclarativeContainer):
    # Core services
    wiring_config = containers.WiringConfiguration(modules=[".api",".app_manager",".api.routes"])
    pubsub_manager = providers.Singleton(PubSubManager)
 
    workflow_queue_manager = providers.Singleton(
        WorkflowQueueManager, 
        pubsub=pubsub_manager,
        workflow_event_router=workflow_event_router
    )
    
    # Create adapter for WorkflowEventSystem
    ingress_event_router = providers.Singleton(IngressEventRouter)

    ingress_manager = providers.Singleton(
        IngressManager,
        event_mode=IngressMode.STREAM,
        uds_path="/tmp/brave.sock",
        ingress_event_router=ingress_event_router
    )

    # Workflow event system
    workflow_queue_manager = providers.Singleton(
        WorkflowQueueManager,
        pubsub=pubsub_manager,
        workflow_event_router=workflow_event_router
    )
    sse_service = providers.Singleton(SSESessionService)
    workflow_sse_manager = providers.Singleton(WorkflowSSEManager, workflow_queue_manager=workflow_queue_manager)
    
    
    
    
    listener_files_service = providers.Singleton(ListenerFilesService)

    analysis_result_parse_service = providers.Singleton(
        AnalysisResultParse,
        sse_service=sse_service,
        listener_files_service=listener_files_service
    )



    # App manager with injected dependencies
    # app_manager = providers.Singleton(
    #     AppManager,
    #     app=providers.Dependency(instance_of=FastAPI),
    #     workflow_event_system=workflow_event_system
    # )
    
