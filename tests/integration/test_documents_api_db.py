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

        assert response.status_code==200
        assert recieved_document["title"]==valid_create_document_payload.title
        assert recieved_document["content"]==valid_create_document_payload.content

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

class TestGetSpecificVersion:

    def test_get_succesful(self, create_db_session, valid_create_document_payload):
        new_document=documents.create_new_document(create_db_session, valid_create_document_payload)
                
        update_payload_scenario=documents_schemas.DocumentUpdate(title="changed title", content="changed content")
        updated_document = documents.update_document(session = create_db_session,
                                                    document_id= new_document.id,
                                                    update_payload=update_payload_scenario)

        document_id=updated_document.id
        version_number=updated_document.version
        response = client.get(
            f"/documents/{document_id}/version/{version_number}"
        )

        response_data = response.json()

        assert response.status_code == 202
        assert response_data["id"] == str(document_id)
        assert response_data["version"] == int(version_number)
