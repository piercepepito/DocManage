from pydantic import BaseModel, Field, ConfigDict

from uuid import UUID
from datetime import datetime

from app.databases.models import Documents

class DocumentResponse(BaseModel):
    """
    The expected API response when creating a document
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    content: str
    version: int
    created_at: datetime
    updated_at: datetime

class DocumentCreate(BaseModel):
    """
    Data supplied when creating a document
    """
    title: str
    content: str

class DocumentUpdate(BaseModel):
    """
    Data supplied when updating a document
    """
    title: str | None = None
    content: str | None = None

class WebhookSignatureSchema(BaseModel):
    """
    The validation schema used for app.webhook.sender py, create_signature function
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    secret_key: str = Field(min_length= 32, max_length= 1024, description="secret key between company and DocView")
    payload_docs: Documents = Field(description="an ORM Documents object")