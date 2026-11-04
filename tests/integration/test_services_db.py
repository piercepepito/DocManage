import pytest
from app import main

from app.schemas import documents_schemas

from fastapi.testclient import TestClient
client = TestClient(app=main.client_api)

@pytest.mark.integration
class TestDocDiffAPI:
    def test_successful(self, valid_create_document_payload):
        #create a document
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

        #update the document
        input_payload["title"]="this is a new title"
        input_payload["content"]="this is new content"
        updated_doc = client.patch(
            f"/documents/{document_id}",
            json=input_payload
        )
        updated_doc_response = updated_doc.json()

        old_version_number = doc_response["version"]
        new_version_number = updated_doc_response["version"]

        endpoint_url = f"/documents/{document_id}/versions/diff?old_version={old_version_number}&new_version={new_version_number}" 
        print(document_id)
        print(endpoint_url)
        response = client.get(
            endpoint_url
        )

        assert response.status_code == 200
