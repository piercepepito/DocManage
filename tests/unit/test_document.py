from unittest.mock import patch, Mock
import pytest

from sqlalchemy.exc import DBAPIError, NoResultFound
from sqlalchemy.orm.exc import StaleDataError

from app.routers import documents, exceptions

import uuid

class TestDocumentCreate:
    @patch("app.routers.documents.Session")
    def test_dberror(self, mock_db, valid_create_document_payload):
        """
        Validate the creates the create_new_document function if it raises the proper dbapierror.
        """
        mock_db.commit.side_effect = DBAPIError(
            statement= "",
            params = [],
            orig=Exception("unable to connect to database")
        )

        with pytest.raises(exceptions.DatabaseStorageError) as e:
            documents.create_new_document(session= mock_db,
                                        document_payload=valid_create_document_payload)

        assert "Failed to save record due to a system error" in str(e.value)

        mock_db.rollback.assert_called_once_with()

    @patch("app.routers.documents.Session")
    def test_general_error(self, mock_db, valid_create_document_payload):
        """
        Validate that the error is the general exception error
        """
        mock_db.commit.side_effect = Exception()

        with pytest.raises(exceptions.DatabaseStorageError) as e:
            documents.create_new_document(session=mock_db,
                                        document_payload=valid_create_document_payload)

        assert "unexpected application error occured" in str(e.value)

        mock_db.rollback.assert_called_once_with()

class TestGetDocument:
    @patch("app.routers.documents.Session")
    def test_no_result_error(self, mock_session):
        """
        validates that the NoResultFound error will occur
        """
        random_uuid = uuid.uuid4()

        mock_session.execute.return_value.scalars.return_value.all.return_value = []

        with pytest.raises(exceptions.NoDocumentFound) as e:
                documents.get_document(mock_session, document_id=random_uuid)

        assert f"Unable to find document id: {random_uuid}" in str(e.value)

    @patch("app.routers.documents.Session")
    def test_database_error(self, mock_session):
        random_uuid = uuid.uuid4()

        mock_session.execute.return_value.scalars.return_value.all.side_effect = DBAPIError(
            statement="",
            params=[],
            orig=Exception("database error occured while retrieving document")
        )

        with pytest.raises(exceptions.DatabaseStorageError) as e:
            documents.get_document(mock_session,
                                   document_id=random_uuid)

        assert "Failed to retrieve document due to database error" in str(e.value)

    @patch("app.routers.documents.Session")
    def test_general_exception(self, mock_session):
        random_uuid = uuid.uuid4()

        mock_session.execute.return_value.scalars.return_value.all.side_effect = Exception()

        with pytest.raises(exceptions.DatabaseStorageError) as e:
            documents.get_document(session=mock_session,
                                   document_id=random_uuid)

        assert "An unexepected application error occurred while retrieving document" in str(e.value)

class TestUpdateDocument:
    @patch("app.routers.documents.Session")
    def test_update_no_document(self, mock_session, valid_create_document_payload):
        """
        validates that the update document function would return the proper NoResultFound Error
        """
        random_id=uuid.uuid4()

        mock_session.execute.return_value.scalar_one.side_effect = NoResultFound()

        with pytest.raises(exceptions.NoDocumentFound) as e:
            documents.update_document(session=mock_session,
                                      document_id=random_id,
                                      update_payload=valid_create_document_payload)

        assert "Unable to find the document while updating it" in str(e.value)

        mock_session.rollback.assert_not_called()

    @patch("app.routers.documents.Session")
    def test_update_stale_data_error(self, mock_session, valid_create_document_payload):
        random_id = uuid.uuid4()

        mock_db_doc = Mock()
        mock_db_doc.title = valid_create_document_payload.title + "some changes"
        mock_db_doc.content = valid_create_document_payload.content
        mock_session.execute.return_value.scalar_one.return_value = mock_db_doc

        mock_session.commit.side_effect = StaleDataError()

        with pytest.raises(exceptions.DocumentConflictError) as e:
            documents.update_document(session=mock_session,
                                      document_id=random_id,
                                      update_payload=valid_create_document_payload)

        assert "This document was modified by another user while you were editing. Please refresh the page and save again." in str(e.value)

        mock_session.rollback.assert_called_once_with()

    @patch("app.routers.documents.Session")
    def test_update_database_error(self, mock_session, valid_create_document_payload):
        """
        Validates that the database error would activate
        """
        random_id = uuid.uuid4()

        mock_updated_document = Mock()
        mock_updated_document.title = valid_create_document_payload.title + "something changed"
        mock_updated_document.content = valid_create_document_payload.content
        mock_session.execute.return_value.scalar_one.return_value = mock_updated_document

        mock_session.commit.side_effect = DBAPIError(
            statement="",
            params=[],
            orig=Exception("database error occured while updating document")
        )

        with pytest.raises(exceptions.DatabaseStorageError) as e:
            documents.update_document(session=mock_session,
                                      document_id=random_id,
                                      update_payload=valid_create_document_payload)

        assert "Failed to update document due to database error" in str(e.value)

        mock_session.rollback.assert_called_once_with()

    @patch("app.routers.documents.Session")
    def test_update_general_exception(self, mock_session, valid_create_document_payload):
        """
        validates the catch all exception
        """
        random_id = uuid.uuid4()

        mock_updated_document = Mock()
        mock_updated_document.title = valid_create_document_payload.title + "changed data"
        mock_updated_document.content = valid_create_document_payload.content
        mock_session.execute.return_value.scalar_one.return_value = mock_updated_document

        mock_session.commit.side_effect = Exception()

        with pytest.raises(exceptions.DatabaseStorageError) as e:
            documents.update_document(session=mock_session,
                                      document_id=random_id,
                                      update_payload=valid_create_document_payload)

        assert "An unexpected error ocured while updating the document" in str(e.value)
        
        mock_session.rollback.assert_called_once_with()
        
class TestGetSpecificDocVersion:
    @patch("app.routers.documents.Session")
    def test_no_result_found(self, mock_session):
        mock_session.execute.return_value.scalar_one.side_effect = NoResultFound()

        mock_doc_id = uuid.uuid4()
        with pytest.raises(exceptions.DatabaseStorageError) as e:
            documents.get_specific_document_version(version=3,
                                                    document_id=mock_doc_id,
                                                    session=mock_session)
            
        assert "Unable to find the document with its specific version. Please check the document id and version" in str(e.value)

    @patch("app.routers.documents.Session")
    def test_db_api_error(self, mock_session):
        mock_session.execute.return_value.scalar_one.side_effect = DBAPIError(
            statement="",
            params=[],
            orig=Exception("database error occured while updating document")
        )

        mock_doc_id=uuid.uuid4()
        with pytest.raises(exceptions.DatabaseStorageError) as e:
            documents.get_specific_document_version(version=2,
                                                    document_id=mock_doc_id,
                                                    session=mock_session)

        assert "Database error occured while trying to retrieve data" in str(e.value)

    @patch("app.routers.documents.Session")
    def test_general_exception(self, mock_session):
        mock_session.execute.return_value.scalar_one.side_effect = Exception()

        mock_doc_id=uuid.uuid4()
        with pytest.raises(exceptions.DatabaseStorageError) as e:
            documents.get_specific_document_version(version=2,
                                                    document_id=mock_doc_id,
                                                    session=mock_session)