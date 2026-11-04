from app.databases import models

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError
from sqlalchemy.exc import DBAPIError, NoResultFound

import logging
from app.routers import exceptions

from app.schemas import documents_schemas
from uuid import UUID

logger = logging.getLogger(__name__)

def create_new_document(session: Session, 
                        document_payload: documents_schemas.DocumentCreate) -> models.Documents:
    """
    Save document into database

    Args:
        session: a sql alchemy session
        document_payload: the elements of the document that needs to be saved

    Returns:
        models.Documents: an ORM object using Documents table 

    Raises:
        DatabaseStorageError: If a database engine crash or unforeseen runtime exception 
                prevents the record from being safely committed.
    """
    logger.info(f"Attempting to create document with title: {document_payload.title}")

    try:
        new_document = models.Documents(**document_payload.model_dump())

        session.add(new_document)
        session.commit()
        session.refresh(new_document)

        logger.info(f"Successfully created document with ID: {new_document.id}")

        return new_document
        
    except DBAPIError as e:
        session.rollback()

        logger.exception("Database operation failed during document creation")
        raise exceptions.DatabaseStorageError("Failed to save record due to a system error")

    except Exception as e:
        session.rollback()

        logger.exception("Unexpected error during document creation")
        raise exceptions.DatabaseStorageError("unexpected application error occured")

def get_document(session: Session, document_id: UUID) -> models.Documents:
    """
    Retrieves the contents of the document

    Args:
        document_id
    Returns:
        models.Documents: Documents ORM object
    Raises:
        exceptions.NoDocumentFound: The wrong ID has been used to get the id
        exceptions.DatabaseStorageError: If a database engine crash or unforeseen runtime exception 
                prevents the record from being retrieved.
    """
    try:
        stmt = select(models.Documents).where(
            models.Documents.id == document_id
            )
        result=session.execute(stmt)

        return result.scalar_one()
    
    except NoResultFound as e:
        logger.exception(f"Document lookup failed from id: {document_id}")
        raise exceptions.NoDocumentFound(f"Unable to find document id: {document_id}")
    
    except DBAPIError as e:
        logger.exception("Database error during document lookup")
        raise exceptions.DatabaseStorageError("Failed to retrieve document due to database error")
    
    except Exception as e:
        logger.exception("Unexpected error occured during document retrieval")
        raise exceptions.DatabaseStorageError("An unexepected application error occurred while retrieving document")

def get_specific_document_version(version: int,
                                  document_id: UUID,
                                  session: Session) -> models.Documents:
    logger.info(f"Retrieving the document with id: {document_id} and version: {str(version)}")
    try:
        stmt = select(models.DocumentHistory).where(
            models.DocumentHistory.document_id == document_id,
            models.DocumentHistory.version == version
        )

        document_retrieved_version = session.execute(stmt).scalar_one()
        
        logger.info("Sucessfully retrieved document with its specific version")
        return document_retrieved_version
    
    except NoResultFound as e:
        logger.exception("Unable to retrieve due to invalid document id or version")
        raise exceptions.DatabaseStorageError("Unable to find the document with its specific version. Please check the document id and version")

    except DBAPIError as e:
        logger.exception("A database error occured while retriving document of a specific version")
        raise exceptions.DatabaseStorageError("Database error occured while trying to retrieve data")

    except Exception as e:
        logger.exception("unexpected error occured while trying to retrieve data with its specific version")
        raise exceptions.DatabaseStorageError("Unable to retrieve data due to an unexepected error")

def update_document(session: Session, 
                    document_id: UUID,
                    update_payload: documents_schemas.DocumentUpdate) -> models.Documents:
    """
    Updates the title/content of the document. Once SQL Alchemy finds a change between the returned document and the new payload,
    it will automatically update the table

    Args:
        session: A SQLAlchemy Session
        document_id: the uuid of the document needed to be udpated
        update_payload: the updated contents and title of the newly edited document
    Returns:
        models.Documents: A SQL ORM object
    Raises:
        exceptions.NoDocumentFound: When there is no document found from the id given
        exceptions.DatabaseStorageError: A database error occured
    """

    logger.info(f"Attempting to update document with document id: {document_id}")
    try:
        stmt = select(models.Documents).where(
            models.Documents.id == document_id
        )

        db_document = session.execute(stmt).scalar_one()

        update_data = update_payload.model_dump(exclude_unset=True)

        has_change=False
        for key, new_value in update_data.items():
            if new_value != getattr(db_document, key):
                setattr(db_document, key, new_value)
                has_change =True

        if not has_change:
            logger.info("No new changes found. No need for update")
            return db_document

        session.commit()
        session.refresh(db_document)

        logger.info(f"Succesfully updated document id: {document_id}")
        return db_document
    
    except NoResultFound as e:
        logger.exception(f"Document look up failed from id: {document_id}")
        raise exceptions.NoDocumentFound("Unable to find the document while updating it")

    except StaleDataError as e:
        session.rollback()
        logger.exception("Concurrency conflict while updating database")
        raise exceptions.DocumentConflictError("This document was modified by another user while you were editing. Please refresh the page and save again.")
    
    except DBAPIError as e:
        session.rollback()
        logger.exception("Database error during updating of document")
        raise exceptions.DatabaseStorageError("Failed to update document due to database error")
    
    except Exception as e:
        session.rollback()
        logger.exception("Unexpected error occurred while update the document")
        raise exceptions.DatabaseStorageError("An unexpected error ocured while updating the document")