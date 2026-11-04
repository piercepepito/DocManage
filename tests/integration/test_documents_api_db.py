import pytest

from app.routers import documents

from app.schemas import documents_schemas
from app import main

from fastapi.testclient import TestClient

client = TestClient(app=main.client_api)

@pytest.mark.integration
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

@pytest.mark.integration
class TestGetDocumentDB:
    def test_get_succesful_id(self, valid_create_document_payload):
        new_document_payload=(documents_schemas.DocumentCreate
                              .model_validate(valid_create_document_payload)
                              .model_dump(mode="json"))
        new_document=client.post(
           "/documents",
           json= new_document_payload
        )

        new_document_response=new_document.json()
        document_id=new_document_response["id"]

        response=client.get(f"/documents/{document_id}")
        recieved_document=response.json()

        print(response.status_code)

        assert response.status_code==200
        assert len(recieved_document["docs"]) == 1

@pytest.mark.integration
class TestUpdateDocument:
    def test_succesful(self, valid_create_document_payload):
        input_payload=(
            documents_schemas
            .DocumentCreate
            .model_validate(valid_create_document_payload)
            .model_dump(mode="json")
        )
        new_document=client.post(
            "/documents",
            json=input_payload
        )
        doc_response=new_document.json()
        document_id=doc_response["id"]
        
        input_payload["title"]="this is a new title"
        input_payload["content"]="this is new content"
        response = client.patch(
            f"/documents/{document_id}",
            json=input_payload
        )
        response_data=response.json()

        assert response.status_code==200

        assert response_data["title"]==input_payload["title"]
        assert response_data["content"]==input_payload["content"]

@pytest.mark.integration
class TestGetSpecificVersion:

    def test_get_succesful(self, valid_create_document_payload):
        input_payload = (documents_schemas
                         .DocumentCreate
                         .model_validate(valid_create_document_payload)
                         .model_dump(mode="json"))

        new_document = client.post(
            "/documents",
            json=input_payload
        )
        new_document_response = new_document.json()

        document_id=new_document_response["id"]
        version_number=1
        response = client.get(
            f"/documents/{document_id}/version/{version_number}"
        )

        response_data = response.json()

        assert response.status_code == 202
        assert response_data["document_id"] == str(document_id)
        assert response_data["version"] == int(version_number)
