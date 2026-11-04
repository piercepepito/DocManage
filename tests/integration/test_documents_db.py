import pytest

from app.schemas import documents_schemas
from app.routers import documents

@pytest.mark.integration
class TestCreateDocumentDB:
    def test_create_documents_valid_payload(self, create_db_session, valid_create_document_payload):
        new_document = documents.create_new_document(session= create_db_session, 
                                                    document_payload=valid_create_document_payload)

        assert new_document.id is not None
        assert new_document.version == 1
        assert new_document.title == valid_create_document_payload.title
        assert new_document.content == valid_create_document_payload.content
        assert new_document.created_at is not None
        assert new_document.updated_at is not None

@pytest.mark.integration
class TestGetDocumentDB:
    def test_get_document(self, create_db_session, valid_create_document_payload):
        """
        validates if the function properl gets the document
        """
        new_document= documents.create_new_document(session=create_db_session, 
                                                    document_payload=valid_create_document_payload)
        
        retrieve_document = documents.get_document(session=create_db_session,
                                                   document_id=new_document.id)

        assert retrieve_document.id == new_document.id
        assert retrieve_document.title == valid_create_document_payload.title
        assert retrieve_document.content == valid_create_document_payload.content

@pytest.mark.integration
class TestUpdateDocumentDB:
    @pytest.mark.parametrize(
    "update_payload_scenario, expected_title, expected_content, expected_version", [
        #CASE 1 - nothing changed
        (documents_schemas.DocumentUpdate(), "original title", "original content", 1),
        #CASE 2 - both content and title changed
        (documents_schemas.DocumentUpdate(title="changed title", content="changed content"), "changed title", "changed content",2),
        #CASE 3 - partial change, only title
        (documents_schemas.DocumentUpdate(title="changed title"), "changed title", "original content",2),
        #CASE 4 - partial change, only content
        (documents_schemas.DocumentUpdate(content="changed content"), "original title", "changed content",2)
    ]
    )
    def test_update_document_working(self, 
                                     create_db_session, 
                                     valid_create_document_payload,
                                     update_payload_scenario,
                                     expected_title,
                                     expected_content,
                                     expected_version):
        """
        validates the function by checking across 4 different scenarios: no changes, both title and content have been changed, the title is changed,
        the content is changed.
        """
        
        new_document=documents.create_new_document(create_db_session, valid_create_document_payload)

        
        result = documents.update_document(session = create_db_session,
                                           document_id= new_document.id,
                                           update_payload=update_payload_scenario)

        assert result.title == expected_title
        assert result.content == expected_content
        assert result.version == expected_version

class TestGetSpecificDocumentVersionDB:
    def test_specific_version_succesful(self, create_db_session, valid_create_document_payload):
        new_document=documents.create_new_document(create_db_session, valid_create_document_payload)
        
        update_payload_scenario=documents_schemas.DocumentUpdate(title="changed title", content="changed content")
        updated_document = documents.update_document(session = create_db_session,
                                                   document_id= new_document.id,
                                                   update_payload=update_payload_scenario)
        
        result = documents.get_specific_document_version(version = updated_document.version,
                                                         document_id = updated_document.id,
                                                         session=create_db_session)

        assert result.version == updated_document.version
