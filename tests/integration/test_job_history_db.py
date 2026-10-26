import pytest

from app.databases import job_history, jobs
from app.routers import documents

class TestJobHistoryDB:
    def test_create_job_history(self, 
                                create_db_session, 
                                valid_job_payload, 
                                valid_create_document_payload,
                                valid_job_history_payload):
        new_document = documents.create_new_document(session=create_db_session,
                                                     document_payload=valid_create_document_payload)

        valid_job_payload.document_id = new_document.id

        new_job = jobs.create_job_row(job_payload=valid_job_payload,
                                      session=create_db_session)

        valid_job_history_payload.job_id = new_job.id

        new_job_hist = job_history.create_job_history(session = create_db_session,
                                                      job_hist_payload=valid_job_history_payload)

        assert new_job_hist.job_id == new_job.id
        assert new_job_hist.attempt_no == valid_job_history_payload.attempt_no
        assert new_job_hist.id is not None