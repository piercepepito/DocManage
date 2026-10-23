import logging

from app.databases import models

from sqlalchemy.orm import Session

from app.routers.exceptions import DatabaseStorageError
from sqlalchemy.exc import DBAPIError 

logger = logging.getLogger(__name__)

def create_document_history(session: Session,
                            document_payload: models.Documents) -> models.DocumentHistory:
    """
    For any new created or newly updated document, a history of the doc will be created

    Args:
        session: a SQLalchemy session
        document_payload: 
    Returns:
        models.DocumentHistory: a sqlalchemy ORM object with the DocumentHistory schema    
    Raises:
        exceptions.DatabaseStorageError: an error occured while a database error has been done
    """
    logger.info(f"Creating new entry for documenthistorytable for document id: {str(document_payload.id)}")

    try:
        document = {
            ("document_id" if col.name == "id" else col.name) : getattr(document_payload, col.name)
            for col in document_payload.__table__.columns
            if col.name not in ["created_at", "updated_at"]
        }


        history_entry = models.DocumentHistory(**document)

        session.add(history_entry)
        session.commit()
        session.refresh(history_entry)

        logger.info("Succesfully added document into DocumentHistory database")

        return history_entry
    
    except DBAPIError as e:
        session.rollback()
        logger.exception("Unable to update Documenthistory table due to database error")
        raise DatabaseStorageError("unable to update record due to database error")
    
    except Exception as e:
        session.rollback()
        logger.exception("unexpected error while updating database")
        raise DatabaseStorageError("unexpected application occured")

    