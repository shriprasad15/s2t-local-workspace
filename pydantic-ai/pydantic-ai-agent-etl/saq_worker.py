import logging.config
import os
from core.log_config import get_log_config

# Configure logging
logging.config.dictConfig(get_log_config())

if __name__ == "__main__":
    # Wrapper around SAQ's CLI
    # Using the correct module path syntax
    os.system(f"python -m saq app.worker.saq.settings --web --port {os.getenv('SAQ_WEB_PORT', '8081')} --workers {os.getenv('SAQ_WORKERS', '1')}")