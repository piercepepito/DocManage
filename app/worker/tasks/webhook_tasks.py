from app.worker import celery_app
from app.webhook import sender

from app.databases import jobs, job_history
from app.databases import db

from app import config

from app.databases.models import Documents
import requests

from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.schemas import jobs_schemas, job_history_schemas

import logging
logger = logging.getLogger(__name__)

@celery_app.celery_app.task(
        bind=True,
        max_retries=config.SEND_DOCVIEW_MAX_RETRIES,
        retry_backoff=True,
        retry_jitter=True,
        retry_backoff_max=config.SEND_DOCVIEW_RETRY_BACKOFF,
        default_retry_delay=config.SEND_DOCVIEW_DEFAULT_RETRY_DELAY
)
def send_message_queue(self, 
                       send_payload: dict) -> requests.Request:
    """
    Creates a worker function to queue all the sent messages to Docview. All worker history (attempts, and exhausted retries) will be recorded 
    inside the job and job history database. Once the retries have been exhausted, the database will be updated where including the successful, 
    and exhausted retry attempts.

    Args:
        send_payload: the data that should be sent to DocView. It should be a dictionary to be serialized by celery
    Returns:
        response: a Requests object, that shows a sucesful send of data
    Raises:
        requests.exceptions.RequestException: Whenever an request post error occured, it will set up for a retry
    """
    #convert dictionary into an ORM Documents object
    send_payload_input = Documents(**send_payload)

    retry = self.request.retries
    attempt_no = retry + 1

    document_id = send_payload_input.id

    celery_task_id = self.request.id
    logger.info(f"Processing document id: {str(send_payload_input.id)} on queue")

    try:
        #ready the payload
        status="succeeded"
        payload_job = {
            "document_id": document_id,
            "attempt_no": attempt_no,
            "status":status,
            "celery_task_id":celery_task_id,
            "completed_at":datetime.now(timezone.utc)
        }
        job_history_payload = {
            "attempt_no":payload_job["attempt_no"], 
            "status":payload_job["status"]
        }

        response = sender.send_payload(payload=send_payload_input)

        logger.info(f"Succesfully sent document to DocView in {attempt_no} attempts")
        return response

    except requests.exceptions.RequestException  as exc:
        retry_allowed = retry < self.max_retries

        #record errors
        error_message = str(exc)

        payload_job["error_message"]=error_message

        if retry_allowed:
            logger.info(f"Unable to send the document. Retrying: {attempt_no} attempts")
            
            status = "in_flight"
            payload_job["status"] = status
            raise self.retry(exc=exc)
        
        else:
            logger.error("Exhausted retries while sending document to DocView")

            status = "exhausted"
            payload_job["status"] = status
            raise

    finally:
        with db.LocalSession() as session:
            if attempt_no == 1:
                print(payload_job)
                job_create = jobs.create_job_row(session=session,
                                    job_payload=jobs_schemas.JobCreate(**payload_job))
            else:
                get_existing_job=jobs.get_job_by_celery_task(session=session,
                                                             celery_task_id=celery_task_id)

                #updated_job_payload["celery_task_id"]=str(get_existing_job.celery_task_id)
                payload_job["id"] = get_existing_job.id
                print(f"This is the payload: {payload_job}")
                job_create = jobs.update_job(session=session,
                                            updated_job=jobs_schemas.JobUpdate(**payload_job))

            #create new job history
            job_history_payload = {
                "job_id":job_create.id,
                "status":status,
                "attempt_no":attempt_no
            }
            job_history.create_job_history(session=session, 
                                        job_hist_payload=job_history_schemas.JobHistoryCreate(**job_history_payload))