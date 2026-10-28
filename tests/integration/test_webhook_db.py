import pytest

from app.webhook import sender

@pytest.mark.integration
class TestSendMessageLive:
    def test_send_message(self, httpserver, monkeypatch, valid_create_doc_history_payload):
        monkeypatch.setenv(
            "DOCVIEW_URL",
            httpserver.url_for("/docview_dummy")
        )

        
        #create a dummy server
        httpserver.expect_request(
            "/docview_dummy",
            method="POST"
        ).respond_with_json(
            {"message":"message recieved"},
            status=200
        )

        response = sender.send_payload(payload=valid_create_doc_history_payload)

        assert response.status_code == 200
        assert response.json() == {"message":"message recieved"}