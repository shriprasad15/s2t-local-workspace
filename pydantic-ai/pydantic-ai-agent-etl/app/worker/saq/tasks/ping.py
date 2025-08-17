import logging
from saq import Queue

async def ping(ctx, *, correlation_id: str = None):
    try:
        logging.info(f"Starting SAQ ping task. Correlation ID: {correlation_id}")
        result = {"status": "success", "correlation_id": correlation_id}
        logging.info(f"Completed SAQ ping task: {result}")
        return result
    except Exception as e:
        logging.error(f"Error in ping task: {e}")
        raise