import logging
from core.saq import get_saq_queue
from .tasks.ping import ping

# Update startup handler to accept context
async def startup(ctx):
    """Startup handler that accepts context parameter"""
    logging.info("SAQ Worker starting up...")
    logging.info(f"Registered tasks: {[ping]}")

# Update shutdown handler to accept context
async def shutdown(ctx):
    """Shutdown handler that accepts context parameter"""
    logging.info("SAQ Worker shutting down...")

queue = get_saq_queue()
if not queue:
    raise ValueError("SAQ Queue not initialized")

settings = {
    "queue": queue,
    "functions": [ping],
    "concurrency": 10,
    "startup": startup,
    "shutdown": shutdown,
}

# Log settings configuration
logging.info(f"SAQ settings configured with queue: {queue}")
logging.info(f"Registered functions: {[f.__name__ for f in settings['functions']]}") 