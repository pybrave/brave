# workflow_event_system/handlers/workflow_events.py

from dependency_injector.wiring import inject
from brave.api.core.routers.workflow_event_router import WorkflowEventRouter
from dependency_injector.wiring import inject, Provide
from brave.app_container import AppContainer
from brave.api.core.event import WorkflowEvent
@inject
def setup_handlers(router: WorkflowEventRouter = Provide[AppContainer.workflow_event_router]    ):

            
    @router.on_event(WorkflowEvent.ON_FLOW_BEGIN)
    async def on_flow_begin(msg: dict):
        print(f"🚀 [on_flow_begin] {msg['analysis_id']}")

    @router.on_event(WorkflowEvent.ON_FILE_PUBLISH)
    async def on_file_publish(msg: dict):
        print(f"✅ [on_file_publish] {msg['analysis_id']}")




    @router.on_event(WorkflowEvent.ON_PROCESS_COMPLETE)
    async def on_process_complete(msg: dict):
        print(f"🚀 [on_process_complete] {msg['analysis_id']}")


    @router.on_event(WorkflowEvent.ON_FLOW_COMPLETE)
    async def on_flow_complete(msg: dict):
        print(f"🚀 [on_flow_complete] {msg['analysis_id']}")


    @router.on_event(WorkflowEvent.ON_JOB_SUBMITTED)
    async def on_job_submitted(msg: dict):
        print(f"🚀 [on_job_submitted] {msg['job_id']}")

