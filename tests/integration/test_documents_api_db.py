import pytest

from app.schemas import documents_schemas
from app import main

from fastapi.testclient import TestClient

client = TestClient(app=main.client_api)

class TestCreateDocumentDB:
    def test_successful(self, valid_create_document_payload):

        input_payload = (documents_schemas
                         .DocumentCreate
                         .model_validate(valid_create_document_payload)
                         .model_dump(mode="json"))

        response = client.post(
            "/documents",
            json=input_payload
        )
        response_data=response.json()

        
        assert response.status_code==201

        assert response_data["title"] == valid_create_document_payload.title
        assert response_data["content"] == valid_create_document_payload.content