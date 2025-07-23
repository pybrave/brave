import asyncio
from dataclasses import dataclass, field
from typing import Dict, Any
import time

from brave.api.core.pubsub import PubSubManager
from brave.api.core.routers.workflow_event_router import WorkflowEventRouter
from brave.api.core.event import WorkflowEvent

@dataclass
class WorkflowQueue:
    queue: asyncio.Queue
    task: asyncio.Task
    last_active: float = field(default_factory=time.time)
    # subscribers: int = 0

class WorkflowQueueManager:
    def __init__(self, pubsub: PubSubManager, workflow_event_router: WorkflowEventRouter):
        self.workflow_map: dict[str, WorkflowQueue] = {}
        self.pubsub = pubsub
        self.workflow_event_router = workflow_event_router
    

    def register_subscriber(self, topic: str, callback):
        self.pubsub.subscribe(topic, callback)

    def register(self, workflow_id: str):
        if workflow_id not in self.workflow_map:
            queue = asyncio.Queue()
            task = asyncio.create_task(self._consume_loop(workflow_id, queue))
            self.workflow_map[workflow_id] = WorkflowQueue(queue=queue, task=task)
    
 
        

    async def put(self, workflow_id: str, msg: dict):
        self.register(workflow_id)
        wfq = self.workflow_map[workflow_id]
        wfq.last_active = time.time()
        await wfq.queue.put(msg)

    async def dispatch(self, msg: dict):
        workflow_id = msg.get("analysis_id", "global")
        await self.put(workflow_id, msg)

    def get(self, workflow_id: str) -> WorkflowQueue:
        return self.workflow_map[workflow_id]

    async def _consume_loop(self, workflow_id: str, queue: asyncio.Queue):
        while True:
            msg = await queue.get()
            try:
                await self.pubsub.publish(workflow_id, msg)
                
                try:
                    event = WorkflowEvent(msg.get("workflow_event"))
                except ValueError:
                    event = msg.get("workflow_event")
                    print(f"[WorkflowEventRouter] Unknown event type '{event}'", msg)
                    return

                await self.workflow_event_router.dispatch(event,workflow_id,msg)
            except Exception as e:
                print(f"[Consumer ERROR] workflow {workflow_id}: {e}")

    async def cleanup(self, timeout: int = 300):
        now = time.time()
        to_delete = []
        for wf_id, wfq in self.workflow_map.items():
            if  wfq.queue.empty() and (now - wfq.last_active > timeout):
                wfq.task.cancel()
                to_delete.append(wf_id)
            
        for wf_id in to_delete:
            del self.workflow_map[wf_id]
            
            await self.pubsub.publish(wf_id, {"event": "workflow_cleanup", "workflow_id": wf_id})
            # await self.workflow_event_router.dispatch(WorkflowEvent.WORKFLOW_CLEANUP, {"analysis_id": wf_id})
            print(f"[Cleanup] Removed workflow {wf_id}")

    
    async def cleanup_loop(self):
        while True:
            await self.cleanup()
            await asyncio.sleep(10)
