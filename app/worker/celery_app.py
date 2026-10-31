from celery import Celery

import os

from app import config

IN_DOCKER = os.path.exists('/.dockerenv')
BROKER_HOST = "redis" if IN_DOCKER else "localhost"

generic_url = f'redis://{BROKER_HOST}:6379/0'


celery_app = Celery("sender_worker")

celery_app.conf.update(
    broker_url= generic_url,
    result_backend = generic_url,
    worker_prefetch_multiplier = config.WORKER_PREFETCH_MULTIPLIER,
    task_time_limit = config.TASK_TIME_LIMIT,
    result_expires=config.RESULT_EXPIRES
)

celery_app.autodiscover_tasks(["app//worker"])
