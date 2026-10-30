from app.schemas import jobs_schemas
from app.databases import models

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import DBAPIError

from app.routers import exceptions

from uuid import UUID

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

def update_job(session: Session,
               updated_job:jobs_schemas.JobUpdate) -> models.Jobs:
    """
    Updates an existing job. Only a single job id will be updated.

    Args:
        session: A SQLAlchemy session
        updated_job: the required payload to update the values inside a specific id
    Returns:
        models.Jobs: an ORM object that mimicks the inside of the jobs table
    Raises:
        DatabaseStorageError: If a database engine crash or unforeseen runtime exception 
        prevents the record from being safely committed.
    """
    
    logger.info(f"Updating row of job id: {updated_job.id}")

    try:
        stmt = select(models.Jobs).where(
            models.Jobs.id == updated_job.id
        )
        existing_job = session.execute(stmt).scalar_one()

        updated_job_values=updated_job.model_dump(exclude_unset=True)
        for key, value in updated_job_values.items():
            setattr(existing_job, key, value)

        session.commit()
        session.refresh(existing_job)

        logger.info("Succesfully updated job")
        return existing_job

    except DBAPIError as e:
        session.rollback()

        logger.exception("Database operation failed while updating job")
        raise exceptions.DatabaseStorageError("Failed to update job due to system error")

    except Exception as e:
        session.rollback()

        logger.exception("Unexpected application error occured while updating existing job")
        raise exceptions.DatabaseStorageError("An unexepected error occured while updating job")

def get_job_by_celery_task(session:Session, celery_task_id: UUID) -> models.Jobs:
    """
    Applied when doing retries for the celery worker. Gets the first row of a Job table, by
    filtering using the celery task id.

    Args:
        session: a SQLAlchemy Session
        celery_task_id: A worker celery task id
    Returns:
        models.Jobs: an ORM jobs Model
    Raises:
        exceptions.DatabaseStorageError: an error whenver there is something wrong when doing database operations
    """
    logger.info(f"Retrieving job id from celery task id: {celery_task_id}")

    try:
        stmt = select(models.Jobs).where(
            models.Jobs.celery_task_id==celery_task_id
        )

        existing_job=session.execute(stmt).scalars().first()

        logger.info("Succesfully retrieved job data from celery task")
        return existing_job    

    except DBAPIError as e:
        logger.exception("Database storage error occured while retrieving job")
        raise exceptions.DatabaseStorageError("An error occured while retrieving data from job table")

    except Exception as e:
        logger.exception("An unexcepted error occured while pulling data from Jobs table")
        raise exceptions.DatabaseStorageError("Unexpected applciation error occured while retrieving data from Jobs table")