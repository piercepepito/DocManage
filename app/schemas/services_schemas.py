from pydantic import BaseModel

from uuid import UUID

class DocDiffCreated(BaseModel):
    document_id: UUID
    old_version: int
    new_version: int
    doc_diff: str