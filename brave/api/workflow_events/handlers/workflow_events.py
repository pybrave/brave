# workflow_event_system/handlers/workflow_events.py

from brave.app_container import AppContainer
from brave.api.core.workflow_event_router import WorkflowEventRouter
from dependency_injector.wiring import inject, Provide


@inject 
def setup_handlers(router: WorkflowEventRouter = Provide[AppContainer.workflow_event_router]):

            
    @router.on_event("flow_begin")
    async def on_flow_begin(msg: dict):
        print(f"🚀 [flow_begin] {msg['workflow_id']}")

    @router.on_event("process_complete")
    async def on_complete(msg: dict):
        print(f"✅ [completed] {msg['workflow_id']}")

    @router.on_event("process_error")
    async def on_error(msg: dict):
        print(f"❌ [error] {msg['workflow_id']}")

    @router.on_event("onProcessComplete")
    async def on_process_complete(msg: dict):
        print(f"✅ [onProcessComplete] {msg['workflow_id']}")

    @router.on_event("job_submitted")
    async def on_job_submitted(msg: dict):
        print(f"🚀 [job_submitted] {msg['job_id']}")

    @router.on_event("job_submitted")
    async def on_job_submitted2(msg: dict):
        print(f"🚀 [job_submitted] {msg['job_id']}")

