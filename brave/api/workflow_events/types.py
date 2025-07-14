from typing import TypedDict, Optional

class EventMessage(TypedDict):
    workflow_id: str
    event: str
    timestamp: str
    msg: Optional[str]
    level: Optional[str]
