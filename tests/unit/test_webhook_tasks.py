import pytest
from unittest.mock import Mock, patch

from app.worker.tasks import webhook_tasks

from app.schemas import documents_schemas

from uuid import uuid4

from app.worker import celery_app
import requests

class TestWebhookWorker:
    @patch("app.worker.tasks.webhook_tasks.job_history")
    @patch("app.worker.tasks.webhook_tasks.jobs")
    @patch("app.worker.tasks.webhook_tasks.sender")
    def test_success_first_try(self, mock_send, mock_jobs, mock_job_history,
                               valid_create_doc_history_payload):
        '''
        Validates that is should run in a single pass
        '''
        #mock_jobs
        mock_job_response = Mock()
        mock_job_response.id = uuid4()

        mock_jobs.create_job_row.return_value = mock_job_response

        #mock job history
        mock_job_history.create_job_history.return_value = Mock()
        
        #mock send payload func
        mock_response = Mock()
        mock_response.status_code = 200

        mock_send.send_payload.return_value = mock_response

        #convert object to dictionary
        send_input = (
                documents_schemas.DocumentResponse
                .model_validate(valid_create_doc_history_payload)
                .model_dump(exclude_unset=True, mode="json")
        )
        
        response = webhook_tasks.send_message_queue.apply(kwargs={"send_payload":send_input})
        
        assert response.result.status_code == 200

        mock_jobs.create_job_row.assert_called_once()
        mock_jobs.update_job.assert_not_called()
        mock_job_history.create_job_history.assert_called_once()

    @patch("app.worker.tasks.webhook_tasks.job_history")
    @patch("app.worker.tasks.webhook_tasks.jobs")
    @patch("app.worker.tasks.webhook_tasks.sender")
    def test_unsuccessful(self, mock_sender, mock_job, mock_job_history,
                          valid_create_doc_history_payload):
        #mock job
        mock_job_response=Mock()
        mock_job_response.id=uuid4()
        mock_job_response.celery_task_id=uuid4()

        mock_job.create_job_row.return_value=mock_job_response
        mock_job.update_job.return_value=mock_job_response
        mock_job.get_job_by_celery_task.return_value=mock_job_response
        
        #mock job history
        mock_job_hist_response=Mock()
        mock_job_history.create_job_history.return_value=mock_job_hist_response

        #mock sending
        max_retries=20
        retry_list= [requests.exceptions.RequestException()]*max_retries
        mock_sender.send_payload.side_effect = retry_list

        #convert ORM Document into dictionary
        input_payload=(documents_schemas.DocumentResponse
                       .model_validate(valid_create_doc_history_payload)
                       .model_dump(exclude_unset=True, mode="json"))

        result = webhook_tasks.send_message_queue.apply(args=[input_payload], throw=False)
        
        assert result.failed()
        assert isinstance(result.result, requests.exceptions.RequestException)

        assert mock_job.create_job_row.call_count == 1

        assert mock_job.get_job_by_celery_task.call_count==5
        assert mock_job.update_job.call_count==5

        assert mock_sender.send_payload.call_count == 6
        assert mock_job_history.create_job_history.call_count == 6

    @patch("app.worker.tasks.webhook_tasks.job_history")
    @patch("app.worker.tasks.webhook_tasks.jobs")
    @patch("app.worker.tasks.webhook_tasks.sender")
    def test_retry_without_exhaust(self, mock_sender, mock_job,
                                   mock_job_history, valid_create_doc_history_payload):

        #mock sender
        mock_sender_response = Mock()
        retry_list = [requests.exceptions.HTTPError("HTTP Error"),
                      requests.exceptions.Timeout("Timeout Error"),
                      requests.exceptions.ConnectionError("Connection Erro"),
                      mock_sender_response]
        mock_sender.send_payload.side_effect= retry_list

        #mock job
        mock_job_response = Mock()
        mock_job_response.id = uuid4()
        mock_job_response.celery_task_id=uuid4()
        
        mock_job.create_job_row.return_value = mock_job_response
        mock_job.get_job_by_celery_task.return_value = mock_job_response
        mock_job.update_job.return_value = mock_job_response

        #mock job history
        mock_job_history.create_job_history.return_value = Mock()

        #convert from Document object to dictionary
        worker_input_payload = (
            documents_schemas.DocumentResponse
            .model_validate(valid_create_doc_history_payload)
            .model_dump(exclude_unset=True, mode="json")
            )

        response = webhook_tasks.send_message_queue.apply(args=[worker_input_payload],
                                                          throw=False)

        assert response.result == mock_sender_response

        assert mock_job.create_job_row.call_count == 1

        assert mock_job.get_job_by_celery_task.call_count == 3
        assert mock_job.update_job.call_count == 3

        assert mock_job_history.create_job_history.call_count==4
        

