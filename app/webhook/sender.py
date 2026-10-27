import hmac
import hashlib

import json

from app.databases.models import Documents
from app.schemas import documents_schemas
from app import config

from pydantic import ValidationError
from app.webhook import exceptions

import requests

import time

from dotenv import load_dotenv
import os
load_dotenv()
SECRET = os.getenv("DOCVIEW_SECRET", "")

import logging
logger = logging.getLogger(__name__)

def create_signature(payload: Documents, 
                     secret: str = SECRET) -> str:
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

def send_payload(payload: Documents) -> requests.Response:
    """
    Sends the saved document to DocView for preview of documents

    Args:
        payload: the document payload 

    Returns:
        response: a Response object, showing the output of the request.post command
    Raises:
        requests.exceptions.HTTPError: raises when raise_for_status sees an error
        requests.exceptions.ConnectionError: cannot get a proper connection to DocView
        requests.exceptions.Timeout: Waited too long and timedout
        requests.exceptions.RequestException: any unexpected errors
    """
    logger.info(f"Attempting to send payload to DocView")

    try:
        #create unix timestamp
        timestamp = int(time.time())
        #create signature
        signature = create_signature(payload)
        
        #create headers
        headers = {
            "Content-Type":"application/json",
            "X-Signature":signature,
            "X-Webhook-Timestamp":timestamp
        }

        #validate and transform payload to pythn dictionary
        validated_payload=documents_schemas.DocumentResponse.model_validate(payload)
        input_payload = validated_payload.model_dump(mode="json")

        response = requests.post(url=os.getenv("DOCVIEW_URL", ""),
                                headers= headers,
                                timeout= config.send_request_timeout,
                                json=input_payload)

        response.raise_for_status()

        logger.info("Succesfully sent data to DocView")

        return response
    
    except requests.exceptions.HTTPError as e:
        logger.exception("Failed to send data to DocView")
        raise
    except requests.exceptions.ConnectionError as e:
        logger.exception("Failed to connect to DocView")
        raise
    except requests.exceptions.Timeout as e:
        logger.exception("DocView had a timed out request")
        raise
    except requests.exceptions.RequestException as e:
        logger.exception("An unexpected error occured while sending data to DocView")
        raise