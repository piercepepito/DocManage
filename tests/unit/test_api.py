import pytest
from unittest.mock import Mock, patch

from app import main

from sqlalchemy.exc import DBAPIError, NoResultFound
from sqlalchemy.orm.exc import StaleDataError

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.schemas import documents_schemas

import uuid

client = TestClient(app=main.client_api, raise_server_exceptions=False)

class TestCreateDoc:
    @patch("app.main.documents")
    def test_db_api_error(self, mock_documents,
                          create_db_session, valid_create_document_payload):

        mock_documents.create_new_document.side_effect=DBAPIError(
            statement= "",
            params = [],
            orig=Exception("unable to connect to database")
        )
        
        with pytest.raises(HTTPException) as e:
            main.create_document(db=create_db_session, document=valid_create_document_payload)

        assert e.value.status_code == 500
        assert e.value.detail == "database connection error"

    @patch("app.main.document_history")
    @patch("app.main.documents")
    def test_db_no_result_found(self, mock_document, mock_doc_hist,
                                create_db_session, valid_create_document_payload):
        mock_document_response=Mock()
        mock_document.create_new_document.return_value=mock_document_response
        
        mock_doc_hist.create_document_history.side_effect=StaleDataError()
        
        with pytest.raises(HTTPException) as e:
            main.create_document(db=create_db_session, document=valid_create_document_payload)

        assert e.value.status_code==409
        assert e.value.detail=="Unable to update the document"

    @patch("app.main.documents")
    def test_exception(self, mock_documents, valid_create_document_payload):
        mock_documents.create_document.side_effect=Exception()
        
        input_payload=(documents_schemas.DocumentCreate
                       .model_validate(valid_create_document_payload)
                       .model_dump(mode="json"))

        response=client.post(
            "/documents",
            json=input_payload
        )
        response_data=response.json()

        assert response.status_code==500

        assert response_data["error"]["code"] == "Internal server error"
        assert response_data["error"]["message"] == "unexpected error occurred"

class TestGetDoc:
    @patch("app.main.documents")
    def test_db_api_error(self, mock_documents, create_db_session):
        mock_documents.get_document.side_effect = DBAPIError(
            statement= "",
            params = [],
            orig=Exception("unable to connect to database")
        )

        mock_doc_id = uuid.uuid4()
        with pytest.raises(HTTPException) as e:
            main.get_document(document_id=mock_doc_id,
                              db=create_db_session)

        assert e.value.status_code==500
        assert e.value.detail=="Unable to reach for document due to internal server error"

    @patch("app.main.documents")
    def test_no_result_found_error(self, mock_document,
                                   create_db_session):
        
        mock_document.get_document.side_effect=NoResultFound("Unable to find document")

        mock_id=uuid.uuid4()
        with pytest.raises(HTTPException) as e:
            main.get_document(db=create_db_session,
                              document_id=mock_id)

        assert e.value.status_code==404
        assert e.value.detail==f"Unable to find document: {mock_id}"

    @patch("app.main.documents")
    def test_general_exception(self, mock_document):
        mock_document.get_document.side_effect=Exception()
        
        mock_id=uuid.uuid4()
        response = client.get(
            f"documents/{mock_id}"
        )

        response.status_code==500

class TestUpdateDocument:
    @patch("app.main.documents")
    def test_db_api_error(self, mock_document,
                          create_db_session, valid_create_document_payload):
        mock_document.update_document.side_effect = DBAPIError(
            statement= "",
            params = [],
            orig=Exception("unable to connect to database")
        )

        mock_id = uuid.uuid4()
        with pytest.raises(HTTPException) as e:
            main.edit_document(session=create_db_session,
                               document_id=mock_id,
                               document=valid_create_document_payload)

        assert e.value.status_code==500
        assert e.value.detail=="unable to save document. please try again later."

    @patch("app.main.documents")
    def test_stale_data(self, mock_document,
                        create_db_session, valid_create_document_payload):

        mock_document.update_document.side_effect=StaleDataError()

        mock_id=uuid.uuid4()
        with pytest.raises(HTTPException) as e:
            main.edit_document(session=create_db_session,
                               document=valid_create_document_payload,
                               document_id=mock_id)

        assert e.value.status_code==409
        assert e.value.detail=="unable to update because of stale data"

    @patch("app.main.documents")
    def test_no_result_found(self, mock_document,
                             create_db_session, valid_create_document_payload):
        mock_document.update_document.side_effect=NoResultFound()

        mock_id=uuid.uuid4()
        with pytest.raises(HTTPException) as e:
            main.edit_document(session=create_db_session,
                               document_id=mock_id,
                               document=valid_create_document_payload)

        assert e.value.status_code==404
        assert e.value.detail=="unable to find the document"

    @patch("app.main.documents")
    def test_general_exception(self, mock_document, valid_create_document_payload):

        mock_document.update_document.side_effect=Exception()

        mock_id=uuid.uuid4()

        input_payload=documents_schemas.DocumentCreate.model_validate(valid_create_document_payload).model_dump(mode="json")
        response = client.patch(
            f"documents/{mock_id}",
            json=input_payload
        )
        
        assert response.status_code==500