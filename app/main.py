from fastapi import FastAPI, status, HTTPException, Request, Depends
from fastapi.responses import JSONResponse

from app.schemas.documents_schemas import DocumentResponse, DocumentCreate, DocumentUpdate, DocumentHistResponse
from app.schemas import services_schemas

from app.databases import db

from app.routers import documents, document_history
from app.services import document_diff
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
def global_exception_handler(
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
    Creates document and assign each document an intial ID and version. Also updates the Docoument History table.

    Args:
        document: a pydantic object
        db: a sqlalchemy session
    Raises:
        HTTPException (500): An internal server error whenever something wrong happened while trying to create anew row inside the database
        HTTPException (409): An error occuring while trying to update the document history table
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
    document: DocumentUpdate,
    session: Session = Depends(db.get_db)
    ):
    """
    Update document and increment its version. Updates the existing document id data (content and title) and creates a new document history row.

    Args:
        document_id: the document being reffered to
        document: the actual document
        session: A sqlaclhemy sesion
    Raises:
        HTTPException(409): Whenever a concurrency issue of two people saving the document at the same time
        HTTPException(404): Unable to find the proper document
        HTTPException(500): A databases error that occured while trying to update both document and document history tables

    
    """
    logging.info(f"Updating existing document: {document_id}")
    try:
        response=documents.update_document(session=session,
                                           document_id=document_id,
                                           update_payload=document)

        document_history.create_document_history(session=session, document_payload=response)
        
        logging.info("Successfully updateed document")
        return response
    
    except StaleDataError as e:
        logger.exception("Stale data while trying to update it.")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="unable to update because of stale data"
        )

    except NoResultFound as e:
        logger.exception("unabel to find the document")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="unable to find the document"
        )

    except DBAPIError as e:
        logger.exception("Unable to update document due to a server error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="unable to save document. please try again later."
        )

@client_api.get(
    "/documents/{document_id}/version/{version_number}",
    response_model=DocumentHistResponse,
    status_code=status.HTTP_202_ACCEPTED
)
def get_specific_version_document(version_number: int,
                                  document_id: UUID,
                                  session: Session = Depends(db.get_db)):
    """
    Gets the speicified version of a document

    Args:
        version_number: the version being specified
        document_id: the document being searched for
        session: a sqlaclhemy sesion
    Raises:
        HTTPException (404): Cannot find the document from the document id and version number combintation
        HTTPException (500): Whenever a database error occured while treying to retrieve the document
    """
    logger.info(f"Retrieving document id: {document_id} of version {version_number}")
    try:
        retrieved_specific_document=documents.get_specific_document_version(version=version_number,
                                                                            document_id=document_id,
                                                                            session=session)

        logger.info("Succesfully retrieved document")
        return retrieved_specific_document
    
    except NoResultFound as e:
        logger.exception("No result found while searching for the document")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unable to find the data. Please check the document id or the version"
        )

    except DBAPIError as e:
        logger.exception("Unable to process due to an internal server error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process due to an internal server error"
        )
    
@client_api.get(
    "/documents/{document_id}/versions/diff",
    response_model= services_schemas.DocDiffCreated,
    status_code = status.HTTP_200_OK,
)
def create_doc_diff(document_id: UUID,
                    old_version: int,
                    new_version: int,
                    session: Session = Depends(db.get_db)):
    """
    Get the difference between 2 version of the same document

    Args:
        document_id: the id of teh document 
        old_version: the version being compared as reference point
        new_version: the version being compared to
        session: a SQLAlchemy Session
    Raises:
        HTTPException (404): Whenever the combintation of both document id and version does not exist
        HTTPException (500): An internal database error while trying to retrieve the data
    
    """
    logger.info(f"Retrieving document id: {document_id} of the following versions: {old_version} and {new_version}")
    try:
        old_doc=documents.get_specific_document_version(version=old_version,
                                                        document_id=document_id,
                                                        session=session)
        new_doc=documents.get_specific_document_version(version=new_version,
                                                        document_id=document_id,
                                                        session=session)

        doc_diff = document_diff.compare_docs(old_document=old_doc,
                                              new_document=new_doc)

        logger.info("Succesfully recieved specific version of the document")
        
        response = {
            "document_id":document_id,
            "old_version": old_version,
            "new_version": new_version,
            "doc_diff":doc_diff
        }

        return response
    
    except NoResultFound as e:
        logger.exception("No data returned while retrieving document")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unable to find the data given the document id and version"
        )
    except DBAPIError as e:
        logger.exception("Database error occured while retrieving data")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error occured while retrieving the data"
        )