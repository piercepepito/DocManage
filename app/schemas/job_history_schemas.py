from pydantic import BaseModel

from uuid import UUID

from typing import Literal
JobStatus=Literal["pending", "in_flight", "succeeded", "exhausted"]

class JobHistoryCreate(BaseModel):
    job_id: UUID
    attempt_no: int
    status: JobStatus