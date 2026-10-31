send_request_timeout = (3,10)

#number of tasks a worker gets per batch
WORKER_PREFETCH_MULTIPLIER = 5
#time limit before the task expires and is forced to close
TASK_TIME_LIMIT = 60
#how long does the result is being kept in the backend
RESULT_EXPIRES = 86400


#config for sending data to DocView
SEND_DOCVIEW_MAX_RETRIES=5
#how long does celery have to wait before doing another retryy
SEND_DOCVIEW_DEFAULT_RETRY_DELAY=10
#how long is the max wait does celery have to wait between retries
SEND_DOCVIEW_RETRY_BACKOFF=100