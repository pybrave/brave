from .workflow_queue import WorkflowQueueManager
from .pubsub import PubSubManager

class EventRouter:
    def __init__(self, pubsub: PubSubManager, wq_manager: WorkflowQueueManager):
        self.pubsub = pubsub
        self.wq_manager = wq_manager

    async def dispatch(self, msg: dict):
        workflow_id = msg.get("workflow_id", "global")
        await self.wq_manager.put(workflow_id, msg)