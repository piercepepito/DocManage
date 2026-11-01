from fastapi import FastAPI, status, HTTPException, Request, Depends
from fastapi.responses import JSONResponse

from app.schemas.documents_schemas import DocumentResponse, DocumentCreate, DocumentUpdate

from app.databases import db

from app.routers import documents, document_history
from app.databases import models

from sqlalchemy.exc import DBAPIError, NoResultFound
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

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
logger=logging.getLogger(__name__)


client_api = FastAPI(
    title="Document management app",
    description="allows the user to do CRUD operations, and check on different history versions",
    version="1.0.0"
)

@client_api.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
):
    logger.exception("An unexpected error occurred: %s %s",
                     request.method,
                     request.url.path)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error":{
                "code": 'Internal server error',
                "message": "unexpected error occurred"
            }
        }
    )

@client_api.post("/documents",
                status_code=status.HTTP_201_CREATED,
                response_model=DocumentResponse)
def create_document(document:DocumentCreate, 
                    db:Session = Depends(db.get_db)):
    """
    Creates document and assign each document an intial ID and version

    No webhook; discover it on the first preview reques
    """
    logger.info("Creating a document")
    try:
        new_document=documents.create_new_document(session=db,
                                                   document_payload=document,)

        update_document_history=(document_history.create_document_history(session=db,
                                                          document_payload=new_document))

        logger.info("Succesfully created the document")

        return new_document

    except DBAPIError as e:
        logger.error("database connection occured while trying to create a new document")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "database connection error"
        )

    except StaleDataError as e:
        logger.exception("Unable to the document")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to update the document"
        )

@client_api.get("/documents/{document_id}",
                status_code=status.HTTP_200_OK,
                response_model=DocumentResponse)
def get_document(
    document_id: UUID,
    db:Session = Depends(db.get_db)
):
    logger.info(f"Searching for document: {document_id}")
    try:
        response=documents.get_document(session=db, document_id=document_id)

        logger.info("Document succesfully found")
        return response
    
    except NoResultFound as e:
        logger.exception("Document cannot be found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unable to find document: {document_id}"
        )

    except DBAPIError as e:
        logger.exception("Database error occured while searching for document")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to reach for document due to internal server error"
        )
    

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
