from pydantic import BaseModel

from uuid import UUID
from datetime import datetime

from typing import Literal, Optional
JobStatus = Literal["pending", "in_flight", "succeeded", "exhausted"]

class JobCreate(BaseModel):
    document_id: UUID
    attempt_no: int
    status: JobStatus = "pending"
    celery_task_id: UUID
    error_message: Optional[str] = None
    next_attempt_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class JobUpdate(BaseModel):
    id:UUID
    attempt_no: int
    status: JobStatus
    celery_task_id:UUID 
    error_message: str
    next_attempt_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None