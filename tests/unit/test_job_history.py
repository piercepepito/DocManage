from unittest.mock import Mock, patch
import pytest

from app.databases import job_history

from sqlalchemy.exc import DBAPIError
from app.routers import exceptions

class TestJobHistoryCreate:
    @patch("app.databases.job_history.Session")
    def test_job_history_db_error(self, mock_session, valid_job_history_payload):

        mock_session.commit.side_effect = DBAPIError(
            statement= "",
            params = [],
            orig=Exception("unable to connect to database")
            )
        with pytest.raises(exceptions.DatabaseStorageError) as e:
            job_history.create_job_history(session=mock_session,
                                           job_hist_payload=valid_job_history_payload)

        assert "Unable to create a new job history record due to a system error" in str(e.value)

        mock_session.rollback.assert_called_once_with()

    @patch("app.databases.job_history.Session")
    def test_job_history_exception_error(self, mock_session, valid_job_history_payload):

        mock_session.commit.side_effect = Exception()

        with pytest.raises(exceptions.DatabaseStorageError) as e:
            job_history.create_job_history(session=mock_session,
                                           job_hist_payload=valid_job_history_payload)

        assert "An unexpected error occured while creating a new record" in str(e.value)

        mock_session.rollback.assert_called_once_with()