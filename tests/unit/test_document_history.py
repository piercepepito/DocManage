from unittest.mock import Mock, patch
import pytest

from app.routers import document_history

from sqlalchemy.exc import DBAPIError
from app.routers.exceptions import DatabaseStorageError

class TestCreateDocumentHistory:
    @patch("app.routers.document_history.Session")
    def test_dbapi_error(self, mock_session, valid_create_doc_history_payload):

        mock_session.commit.side_effect = DBAPIError(
            statement= "",
            params = [],
            orig=Exception("unable to connect to database")
        )

        with pytest.raises(DatabaseStorageError) as e:
            document_history.create_document_history(session=mock_session,
                                                     document_payload=valid_create_doc_history_payload)

        assert "unable to update record due to database error" in str(e.value)

        mock_session.rollback.assert_called_once_with()

    @patch("app.routers.document_history.Session")
    def test_general_error(self, mock_db, valid_create_doc_history_payload):

        mock_db.commit.side_effect = Exception()
        
        with pytest.raises(DatabaseStorageError) as e:
            document_history.create_document_history(session=mock_db,
                                                     document_payload=valid_create_doc_history_payload)

        assert "unexpected application occured" in str(e.value)

        mock_db.rollback.assert_called_once_with()