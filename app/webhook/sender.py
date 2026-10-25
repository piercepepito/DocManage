import hmac
import hashlib

import json

from app.databases.models import Documents
from app.schemas import documents_schemas

from pydantic import ValidationError
from app.webhook import exceptions

from dotenv import load_dotenv
import os
load_dotenv()
SECRET = os.getenv("SECRET", "")

import logging
logger = logging.getLogger(__name__)

def create_signature(payload: Documents, 
                     secret: str = SECRET):
    """
    Creates a signature, and sends the payload to the 3rd party company for document preview

    Args:
        payload: an ORM Documents object, used to send to DocView for previewing of documents
        secret: the secret key shared with the DocView and saved inside the .env file
    Returns:
        signature: using sha256 to hash the payload and the secret key which returns a hexadecimal text string
    Raises:

    """
    try:
        logger.info(f"Creating signature for {payload.id}")

        validate_data = documents_schemas.WebhookSignatureSchema(secret_key=secret, payload_docs=payload)

        secret_key=validate_data.secret_key.encode("utf-8")
        #convert ORM object into bytes
        validated_document = documents_schemas.DocumentResponse.model_validate(validate_data.payload_docs)
        payload_dict = validated_document.model_dump(mode="json")
        payload_bytes=json.dumps(payload_dict, sort_keys=True).encode("utf-8")

        signature = hmac.new(
            key=secret_key,
            msg=payload_bytes,
            digestmod=hashlib.sha256
        ).hexdigest()

        logger.info("Succesfully created signature")

        return signature
    
    except ValidationError as e:
        logger.exception("Configuration or schema validation failed")
        raise exceptions.WebhookSignatureError("Invalid secret key or payload")
    except UnicodeError as e:
        logger.exception("Failed to convert string into bytes")
        raise exceptions.WebhookSignatureError("Payload or secret key contains un-encodable text")
    except TypeError as e:
        logger.exception("Formatting error during payload serialization")
        raise exceptions.WebhookSignatureError("Failed to format the document payload into a valid JSON structure")
    except Exception as e:
        logger.critical(f"Unhandled critical exception in signature module {str(e)}")
        raise exceptions.WebhookSignatureError("An unexpected error occured while creating signature")

def send_payload(signature):
    pass