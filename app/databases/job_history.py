from app.databases.models import JobHistory
from app.routers import exceptions
from app.schemas import job_history_schemas

from sqlalchemy.orm import Session
from sqlalchemy.exc import DBAPIError

import logging
logger=logging.getLogger(__name__)

def create_job_history(session: Session,
                       job_hist_payload: job_history_schemas.JobHistoryCreate) -> JobHistory:
    """
    
    Args:
        session: a SQLAlchemy Session
        job_hist_payload: the necessary input used to create a new job history data row
    Returns:
        JobHistory: An ORM model
    Raises:
        DatabaseStorageError: Whenever a database related error occurs and prevents the record from being executed
    """
    logger.info(f"Creating a Job History record from job_id:{job_hist_payload.job_id}")

    try:
        new_job_history = JobHistory(**job_hist_payload.model_dump())

        session.add(new_job_history)
        session.commit()
        session.refresh(new_job_history)

        logger.info("Succesfully created a job history record")

        return new_job_history

    except DBAPIError as e:
        session.rollback()

        logger.exception("Database operation failed from creating a new job history record")
        raise exceptions.DatabaseStorageError("Unable to create a new job history record due to a system error")
    
    except Exception as e:
        session.rollback()

        logger.exception("Unexpected error while creating a new job history record")
        raise exceptions.DatabaseStorageError("An unexpected error occured while creating a new record")