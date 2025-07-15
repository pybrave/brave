# brave/container.py
from dependency_injector import containers, providers
from brave.api.workflow_events.manager import WorkflowEventSystem
from brave.app_manager import AppManager
from fastapi import FastAPI
from brave.api.core.workflow_event_router import WorkflowEventRouter
from brave.api.workflow_events.workflow_queue import WorkflowQueueManager
from brave.api.core.pubsub import PubSubManager
class AppContainer(containers.DeclarativeContainer):
    app_manager = providers.Singleton(AppManager, app=providers.Dependency(instance_of=FastAPI))
    workflow_event_router = providers.Singleton(WorkflowEventRouter)
    pubsub_manager = providers.Singleton(PubSubManager)
    workflow_queue_manager = providers.Singleton(WorkflowQueueManager, pubsub=pubsub_manager, workflow_event_router=workflow_event_router)
    providers.Singleton(WorkflowEventSystem,queue_manager=workflow_queue_manager,pubsub=pubsub_manager)
    
