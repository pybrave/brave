# brave/container.py
from anyio import Event
from dependency_injector import containers, providers
from brave.api.core.evenet_bus import EventBus
from brave.api.core.routers.analysis_result_router import AnalysisResultRouter
from brave.api.core.routers.workflow_event_router import WorkflowEventRouter
from brave.api.core.workflow_queue import WorkflowQueueManager
from brave.api.core.pubsub import PubSubManager
from brave.api.core.routers.ingress_event_router import IngressEventRouter
from brave.api.ingress.manager import IngressManager
from brave.api.core.workflow_sse import WorkflowSSEManager
from brave.api.service.result_parse.analysis_manage import AnalysisManage
from brave.api.service.result_parse.nextflow_analysis import NextflowAnalysis
from brave.api.service.result_parse.script_analysis import ScriptAnalysis
from brave.api.service.sse_service import SSESessionService
from brave.api.service.analysis_result_parse import AnalysisResultParse
from brave.api.service.listener_files_service import ListenerFilesService
from brave.api.ingress.factory import IngressMode
from brave.api.core.routers.watch_file_event_router import WatchFileEvenetRouter
from brave.api.core.routers.analysis_executer_router import AnalysisExecutorRouter
# from brave.api.executor.factory import get_executor
from brave.api.executor.docker_excutor import DockerExecutor
from brave.api.executor.k8s_executor import K8sExecutor
from brave.api.executor.slurm_executor import SlurmExecutor
from brave.api.executor.local_executor import LocalExecutor
class AppContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    # Core services
    wiring_config = containers.WiringConfiguration(modules=[".api",".app_manager",".api.routes"])
    pubsub_manager = providers.Singleton(PubSubManager)
    workflow_event_router = providers.Singleton(WorkflowEventRouter)
    watchfile_event_router = providers.Singleton(WatchFileEvenetRouter)
    analysis_executer_router = providers.Singleton(AnalysisExecutorRouter)
    analysis_result_router = providers.Singleton(AnalysisResultRouter)


    
    

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
    # workflow_queue_manager = providers.Singleton(
    #     WorkflowQueueManager,
    #     pubsub=pubsub_manager,
    #     workflow_event_router=workflow_event_router
    # )
    sse_service = providers.Singleton(SSESessionService)
    workflow_sse_manager = providers.Singleton(WorkflowSSEManager, workflow_queue_manager=workflow_queue_manager)
    
    event_bus = providers.Singleton(
        EventBus,
    )
    nextflow_analysis = providers.Singleton(NextflowAnalysis,event_bus=event_bus)
    script_analysis = providers.Singleton(ScriptAnalysis,event_bus=event_bus)
    analysis_controller_selector = providers.Selector(
        lambda type: type,  
        script=script_analysis,
        nextflow=nextflow_analysis
    )
    
    
    listener_files_service = providers.Singleton(ListenerFilesService)

    analysis_result_parse_service = providers.Singleton(
        AnalysisResultParse
  
    )
    result_parse_manage= providers.Singleton(AnalysisManage, event_bus=event_bus)
    
 
    docker_executor = providers.Singleton(DockerExecutor,event_bus=event_bus)
    k8s_executor = providers.Singleton(K8sExecutor,event_bus=event_bus)
    slurm_executor = providers.Singleton(SlurmExecutor,event_bus=event_bus)
    local_executor = providers.Singleton(LocalExecutor,event_bus=event_bus)
    job_executor_selector = providers.Selector(
        config.executer_type,
        local=local_executor,
        docker=docker_executor,
        k8s=k8s_executor,
        slurm=slurm_executor
    )
        
    # job_executor  =providers.Singleton(get_executor,"local")

    # App manager with injected dependencies
    # app_manager = providers.Singleton(
    #     AppManager,
    #     app=providers.Dependency(instance_of=FastAPI),
    #     workflow_event_system=workflow_event_system
    # )
    
