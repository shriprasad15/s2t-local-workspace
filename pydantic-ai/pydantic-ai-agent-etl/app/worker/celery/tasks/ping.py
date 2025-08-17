import logging

from core.celery import get_celery_app

app = get_celery_app()


@app.task
def ping():
    logging.info(f"Sample logging from celery ping task")
