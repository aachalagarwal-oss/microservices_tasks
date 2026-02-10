from pydantic import BaseModel
from enum import Enum
from typing import Optional

class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"

class TaskCreate(BaseModel):
    title: str
    description: str
    status: TaskStatus = TaskStatus.pending

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
