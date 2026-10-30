import pytest

from unittest.mock import patch
import uuid

from app.databases import jobs
from app.routers import exceptions

from sqlalchemy.exc import DBAPIError

class TestCreateJob:
    @patch("app.databases.jobs.Session")
    def test_job_dbapi_error(self, mock_session, valid_job_payload):

        mock_session.commit.side_effect = DBAPIError(
            statement= "",
            params = [],
            orig=Exception("unable to connect to database")
        )

        with pytest.raises(exceptions.DatabaseStorageError) as e:
            jobs.create_job_row(valid_job_payload,
                                session=mock_session)

        assert "Failed to create new job due to system error" in str(e.value)

        mock_session.rollback.assert_called_once_with()

    @patch("app.databases.jobs.Session")
    def test_job_exception_error(self, mock_session, valid_job_payload):

        mock_session.commit.side_effect = Exception()

        with pytest.raises(exceptions.DatabaseStorageError) as e:
            jobs.create_job_row(valid_job_payload,
                                session=mock_session)

        assert "An unexpected application error occured while creating a new job" in str(e.value)

        mock_session.rollback.assert_called_once_with()

class TestUpdateJob:

    @patch("app.databases.jobs.Session")
    def test_job_update_db_error(self, mock_session, valid_job_update_payload):

        mock_session.execute.return_value.scalar_one.side_effect = DBAPIError(
            statement= "",
            params = [],
            orig=Exception("unable to connect to database")
        )

        with pytest.raises(exceptions.DatabaseStorageError) as e:
            jobs.update_job(session=mock_session,
                            updated_job=valid_job_update_payload)

        assert "Failed to update job due to system error" in str(e.value)

        mock_session.rollback.assert_called_once_with()

    @patch("app.databases.jobs.Session")
    def test_job_exception(self, mock_session, valid_job_update_payload):

        mock_session.execute.return_value.scalar_one.side_effect = Exception()

        with pytest.raises(exceptions.DatabaseStorageError) as e:
            jobs.update_job(
                session = mock_session,
                updated_job= valid_job_update_payload
            )

        assert "An unexepected error occured while updating job" in str(e.value)

        mock_session.rollback.assert_called_once_with()

class TestRetrieveJob:
    @patch("app.databases.jobs.Session")
    def test_dbapi_error(self, mock_session):
        mock_session.execute.side_effect = DBAPIError(
            statement= "",
            params = [],
            orig=Exception("unable to connect to database")
        )

        celery_id=uuid.uuid4()

        with pytest.raises(exceptions.DatabaseStorageError) as e:
            jobs.get_job_by_celery_task(session=mock_session,
                                        celery_task_id=celery_id
                                        )

        assert "An error occured while retrieving data from job table" in str(e.value)

    @patch("app.databases.jobs.Session")
    def test_exception_error(self, mock_session):
        mock_session.execute.side_effect=Exception()

        celery_id=uuid.uuid4()

        with pytest.raises(exceptions.DatabaseStorageError) as e:
            jobs.get_job_by_celery_task(session=mock_session,
                                        celery_task_id=celery_id)

        assert "Unexpected applciation error occured while retrieving data from Jobs table" in str(e.value)