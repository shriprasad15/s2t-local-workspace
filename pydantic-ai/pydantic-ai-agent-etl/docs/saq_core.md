# SAQ Core Documentation

## Overview
The SAQ core module provides essential functionality for asynchronous task processing using Redis as the message broker. It implements task queuing, processing, and monitoring capabilities.

## Key Components

### Queue Configuration
The core queue configuration in `core/saq.py`:
```python
@cache
def get_saq_queue() -> Queue | None:
    try:
        if settings.REDIS_URL is None:
            logging.error("SAQ disabled due to REDIS_URL not set")
            return None

        queue = Queue.from_url(settings.REDIS_URL)
        logging.info("SAQ queue initiated")
        return queue
    except Exception as e:
        logging.error(f"Failed to initiate SAQ queue: {e}")
        return None
```

### Task Structure
Tasks are implemented as async functions with context and correlation ID:
```python
async def task_name(ctx, *, correlation_id: str = None):
    """
    Args:
        ctx: SAQ context
        correlation_id: Request correlation ID for tracing
    """
    pass
```

### Worker Settings
Worker configuration structure:
```python
settings = {
    "queue": Queue instance,
    "functions": [registered_tasks],
    "concurrency": worker_count,
    "startup": startup_handler,
    "shutdown": shutdown_handler,
}
```

## Best Practices

1. **Task Implementation**
   - Keep tasks small and focused
   - Include correlation ID for tracing
   - Add proper error handling
   - Use structured logging

2. **Queue Management**
   - Monitor queue size
   - Set appropriate concurrency
   - Implement retry strategies
   - Handle backpressure

3. **Monitoring**
   - Use the web UI for active monitoring
   - Check Redis stats regularly
   - Monitor worker health
   - Track task completion rates

4. **Error Handling**
   - Implement proper exception handling
   - Log errors with context
   - Use retry mechanisms
   - Monitor failed tasks

## Usage Example

```python
# Task implementation
async def process_data(ctx, *, data: dict, correlation_id: str = None):
    try:
        logging.info(f"Processing data with correlation ID: {correlation_id}")
        result = await process(data)
        return {"status": "success", "result": result}
    except Exception as e:
        logging.error(f"Processing failed: {str(e)}")
        raise
``` 