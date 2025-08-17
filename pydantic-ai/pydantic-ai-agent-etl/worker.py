import logging.config
import os

from core.celery import get_celery_app
from core.log_config import get_log_config

logging.config.dictConfig(get_log_config())
app = get_celery_app()

if __name__ == "__main__":
    args = ['worker', f'--loglevel={os.environ.get("LOG_LEVEL", "INFO")}']
    app.worker_main(args)
