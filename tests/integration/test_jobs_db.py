from app.databases import jobs
from app.routers import documents
import pytest

class TestJobCreateDB:
    def test_create_new_job(self, valid_job_payload, valid_create_document_payload, create_db_session):
        new_document = documents.create_new_document(session=create_db_session,
                                                     document_payload=valid_create_document_payload)

        valid_job_payload.document_id = new_document.id

        new_job = jobs.create_job_row(job_payload=valid_job_payload,
                                      session=create_db_session)

        assert new_job.status == "pending"
        assert new_job.attempt_no == 2
        assert new_job.document_id == new_document.id
        assert new_job.completed_at == None
        assert new_job.error_message == None