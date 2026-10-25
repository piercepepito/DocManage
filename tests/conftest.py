import pytest

from app.databases.db import get_db

from app.schemas.documents_schemas import DocumentCreate
from app.databases.models import Documents

import uuid
from datetime import datetime

@pytest.fixture
def create_db_session():
    db = next(get_db())
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture
def valid_create_document_payload():
    return DocumentCreate(
        title="original title",
        content="original content"
    )   

@pytest.fixture
def valid_create_doc_history_payload():
    """
    Documents ORM object
    """
    random_id = uuid.uuid4()

    time_now = datetime.now()
    
    return Documents(
        id=random_id,
        title="sample title",
        content="sample content",
        version=1,
        created_at=time_now,
        updated_at=time_now
    )