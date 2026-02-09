from pydantic import BaseModel
from enum import Enum

class TaskStatus(str,Enum):
    pending="pending"
    in_progress="in_progress"
    completed="completed"

class TaskCreate(BaseModel):
    title:str
    description:str
    status:TaskStatus=TaskStatus.pending
    
class TaskResponse(BaseModel):
    title:str
    description:str
    status:str

