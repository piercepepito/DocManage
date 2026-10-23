from app.routers import document_history, documents

class TestDocumentHistoryDB:
    def test_doc_history_db(self, create_db_session, valid_create_document_payload):
        new_document = documents.create_new_document(session= create_db_session, document_payload=valid_create_document_payload)
        
        history_event = document_history.create_document_history(session= create_db_session,
                                                                 document_payload=new_document)

        assert hasattr(history_event, "id")
        assert hasattr(history_event, "document_id")
        assert not hasattr(history_event, "updated_at")

        assert history_event.document_id == new_document.id
        assert history_event.title == valid_create_document_payload.title
        assert history_event.content == valid_create_document_payload.content