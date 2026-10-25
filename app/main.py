from fastapi import FastAPI, status

from app.schemas.documents_schemas import DocumentResponse, DocumentCreate, DocumentUpdate

from uuid import UUID

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(), #output logs to console terminal
        logging.FileHandler("app.log") #save to a file
    ]
)

client_api = FastAPI()

@client_api.post("/documents",
                status_code=status.HTTP_201_CREATED,
                response_model=DocumentResponse)
def create_document(document:DocumentCreate):
    """
    Creates document and assign each document an intial ID and version

    No webhook; discover it on the first preview reques
    """
    title = document.title
    content = document.content
    
    pass


@client_api.patch("/documents/{document_id}",
                status_code=status.HTTP_200_OK,
                response_model=DocumentResponse)
def edit_document(
    document_id: UUID,
    document: DocumentUpdate
    ):
    """
    Update document and increment its version

    Send document-update webhooks to DocView when a document changes.
    """
    pass
