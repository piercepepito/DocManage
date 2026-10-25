from app.schemas import jobs_schemas
from app.databases import models

from sqlalchemy.orm import Session
from sqlalchemy.exc import DBAPIError

from app.routers import exceptions

import logging
logger = logging.getLogger(__name__)

def create_job_row(job_payload: jobs_schemas.JobCreate,
                   session: Session) -> models.Jobs:
    """
    Creates a new job row inside Postgres db

    Args:
        job_payload: expected input to create a job row
        session: a SQL Alchemy Session
    Returns:
        models.Jobs: an ORM object that mimicks the inside of the jobs table
    Raises:
        DatabaseStorageError: If a database engine crash or unforeseen runtime exception 
        prevents the record from being safely committed.

    """
    logger.info(f"Creating job for document_id: {job_payload.document_id}")

    try:
        new_job = models.Jobs(**job_payload.model_dump())

        session.add(new_job)
        session.commit()
        session.refresh(new_job)

        logger.info("Succesfully created job")

        return new_job

    except DBAPIError as e:
        session.rollback()

        logger.exception("Database operation failed from job creation")
        raise exceptions.DatabaseStorageError("Failed to create new job due to system error")

    except Exception as e:
        session.rollback()

        logger.exception("Unexpected error occured while creating new job")
        raise exceptions.DatabaseStorageError("An unexpected application error occured while creating a new job")