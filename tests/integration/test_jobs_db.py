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

class TestJobUpdateDB:

    def test_update_job(self, 
                        create_db_session, 
                        valid_job_payload,
                        valid_job_update_payload,
                        valid_create_document_payload):
        #create a new job
        new_document = documents.create_new_document(session=create_db_session,
                                                document_payload=valid_create_document_payload)

        valid_job_payload.document_id = new_document.id

        new_job = jobs.create_job_row(job_payload=valid_job_payload,
                                      session=create_db_session)
        #update job
        valid_job_update_payload.id = new_job.id

        update_job = jobs.update_job(session=create_db_session,
                                     updated_job=valid_job_update_payload)


        assert update_job.id == new_job.id
        assert update_job.document_id == new_document.id
        assert update_job.attempt_no == valid_job_update_payload.attempt_no
        assert update_job.status == valid_job_update_payload.status
        assert update_job.error_message == valid_job_update_payload.error_message
        assert update_job.next_attempt_at == valid_job_update_payload.next_attempt_at
        assert update_job.completed_at == valid_job_update_payload.completed_at