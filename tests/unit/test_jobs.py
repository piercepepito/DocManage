import pytest

from unittest.mock import patch

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


