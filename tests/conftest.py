import pytest

from app.databases.db import get_db

from app.schemas.documents_schemas import DocumentCreate
from app.schemas import jobs_schemas, job_history_schemas

from app.databases.models import Documents

import uuid
from datetime import datetime, timezone

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

@pytest.fixture
def valid_job_payload():
    return jobs_schemas.JobCreate(
        document_id = uuid.uuid4(),
        attempt_no = 2,
        status = "pending",
        celery_task_id=uuid.uuid4(),
        error_message = None,
        next_attempt_at = None,
        completed_at = None
    )

@pytest.fixture
def valid_job_update_payload():
    return jobs_schemas.JobUpdate(
        id = uuid.uuid4(),
        attempt_no = 3,
        status = "succeeded",
        error_message = "This is an error message",
        next_attempt_at = datetime.now(timezone.utc),
        completed_at = datetime.now(timezone.utc)
    )

@pytest.fixture
def valid_job_history_payload():
    return job_history_schemas.JobHistoryCreate(
        job_id = uuid.uuid4(),
        attempt_no = 3,
        status = "pending"
    )

@pytest.fixture
def invalid_send_message_payload():
    return Documents(
        id="invalid input"
    )