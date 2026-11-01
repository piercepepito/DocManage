import pytest
from unittest.mock import Mock, patch

from app import main

from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm.exc import StaleDataError

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.schemas import documents_schemas

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