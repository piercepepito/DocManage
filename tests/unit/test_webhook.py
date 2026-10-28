from app.webhook import sender
from app.databases.models import Documents

import pytest
from unittest.mock import Mock, patch
from app.webhook import exceptions

from pydantic import ValidationError

import requests

import secrets

class TestWebhookSignature:
    def test_different_payload_same_signature(self, valid_create_doc_history_payload):
        secret_key = secrets.token_hex(32)
        
        original_payload=valid_create_doc_history_payload

        modified_payload = Documents(
            id=original_payload.id,
            title="another title not from the original payload",
            content=original_payload.content,
            version=original_payload.version,
            created_at=original_payload.created_at,
            updated_at=original_payload.updated_at
        )

        signature_1 = sender.create_signature(payload=original_payload, secret=secret_key)
        signature_2 = sender.create_signature(payload=modified_payload, secret=secret_key)

        assert signature_1 != signature_2

    def test_different_secrets(self, valid_create_doc_history_payload):
        secret1 = secrets.token_hex(32)
        secret2 = secrets.token_hex(32)

        signature1 = sender.create_signature(payload=valid_create_doc_history_payload, secret=secret1)
        signature2 = sender.create_signature(payload=valid_create_doc_history_payload, secret=secret2)

        assert signature1 != signature2

    def test_validation_error(self, valid_create_doc_history_payload):
        #secret key should be less than 32 to force a validation error
        secret_fake = secrets.token_hex(16)[:31]

        with pytest.raises(exceptions.WebhookSignatureError) as e:
            sender.create_signature(secret=secret_fake,
                                    payload=valid_create_doc_history_payload)

        assert "Invalid secret key or payload" in str(e.value)

    @patch("app.webhook.sender.documents_schemas")
    def test_unicode_error(self, mock_schema, valid_create_doc_history_payload):
        mock_schema.DocumentResponse.model_validate.side_effect = UnicodeError()
        secret_key = secrets.token_hex(32)
        
        with pytest.raises(exceptions.WebhookSignatureError) as e:
            sender.create_signature(payload=valid_create_doc_history_payload,
                                    secret=secret_key)

        assert "Payload or secret key contains un-encodable text" in str(e.value)

    @patch("app.webhook.sender.json")
    def test_type_error(self, mock_json, valid_create_doc_history_payload):
        mock_json.dumps.side_effect = TypeError()
        
        secret_key=secrets.token_hex(32)

        with pytest.raises(exceptions.WebhookSignatureError) as e:
            sender.create_signature(payload=valid_create_doc_history_payload,
                                    secret=secret_key)

        assert "Failed to format the document payload into a valid JSON structure" in str(e.value)

    @patch("app.webhook.sender.documents_schemas")
    def test_exception(self, mock_schema, valid_create_doc_history_payload):
        mock_schema.WebhookSignatureSchema.side_effect=Exception()
        
        secret_key=secrets.token_hex(32)

        with pytest.raises(exceptions.WebhookSignatureError) as e:
            sender.create_signature(secret=secret_key,
                                    payload=valid_create_doc_history_payload)

        assert "An unexpected error occured while creating signature" in str(e.value)


class TestSendPayload:
    @patch("app.webhook.sender.requests.post")
    def test_succesful_send(self, mock_request_post, valid_create_doc_history_payload):
        mock_response = Mock()
        mock_request_post.return_value = mock_response

        response = sender.send_payload(valid_create_doc_history_payload)

        assert response == mock_response

    @patch("app.webhook.sender.requests.post")
    def test_http_error(self, mock_request_post, valid_create_doc_history_payload):

        mock_request_post.return_value = Mock()
        mock_request_post.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError()

        with pytest.raises(requests.exceptions.HTTPError):
            sender.send_payload(payload=valid_create_doc_history_payload)

        mock_request_post.assert_called_once()
        mock_request_post.return_value.raise_for_status.assert_called_once_with()

    @patch("app.webhook.sender.requests.post")
    def test_connection_error(self, mock_request_post, valid_create_doc_history_payload):
        mock_request_post.side_effect = requests.exceptions.ConnectionError()

        with pytest.raises(requests.exceptions.ConnectionError): 
            sender.send_payload(payload=valid_create_doc_history_payload)

        mock_request_post.return_value.raise_for_status.assert_not_called()

    @patch("app.webhook.sender.requests.post")
    def test_timeout_error(self, mock_request_post, valid_create_doc_history_payload):

        mock_request_post.side_effect = requests.exceptions.Timeout

        with pytest.raises(requests.exceptions.Timeout):
            sender.send_payload(payload=valid_create_doc_history_payload)


        mock_request_post.return_value.raise_for_status.assert_not_called()

    @patch("app.webhook.sender.requests.post")
    def test_request_exception(self, mock_request_post, valid_create_doc_history_payload):

        mock_request_post.side_effect = requests.exceptions.RequestException()

        with pytest.raises(requests.exceptions.RequestException):
            sender.send_payload(valid_create_doc_history_payload)

        mock_request_post.raise_for_status.assert_not_called()


        
        
    #succesful