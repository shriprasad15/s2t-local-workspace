# SAQ Integration Guide

This guide explains how SAQ (Simple Async Queue) is integrated into the FastAPI boilerplate for asynchronous task processing using Redis.

## Overview

SAQ is used to handle asynchronous task processing with Redis. The integration provides:
- Task queuing from API endpoints
- Async task processing
- Correlation ID tracking
- Web UI for monitoring
- Structured logging

## Configuration

SAQ configuration is managed through environment variables:

```env
REDIS_URL=redis://localhost:6379  # Redis connection URL
SAQ_ENABLE=true                   # Enable/disable SAQ integration
SAQ_WEB_PORT=8081                # Web UI port
SAQ_WORKERS=1                    # Number of worker processes
```

## Task Implementation

Tasks use async functions with correlation ID tracking:

```python
# Example task implementation
async def ping(ctx, *, correlation_id: str = None):
    logging.info(f"Processing SAQ ping task. Correlation ID: {correlation_id}")
    return {"status": "success", "correlation_id": correlation_id}
```

## Worker Configuration

SAQ worker settings are configured in `app/worker/saq/settings.py`:

```python
settings = {
    "queue": queue,
    "functions": [ping],
    "concurrency": 10,
    "startup": startup,
    "shutdown": shutdown,
}
```

## Task Publishing

Tasks can be published from API endpoints:

```python
@router.get("/ping")
async def ping(request: Request):
    correlation_id = correlation_id_ctx_var.get()
    
    if settings.SAQ_ENABLE:
        queue = get_saq_queue()
        if queue:
            await queue.enqueue("ping", correlation_id=correlation_id)
    
    return {"version": settings.APP_VERSION, "message": "pong"}
```

## Correlation ID

The correlation ID is automatically:
1. Generated for each incoming HTTP request
2. Added to the context using ContextVar
3. Passed to SAQ tasks
4. Logged with all log messages

This enables request tracking across the entire system.

## Monitoring

### Web Interface
Access the SAQ web UI at `http://localhost:8081` to:
- Monitor active tasks
- View task history
- Check worker status

### Redis Inspection
Monitor tasks using Redis CLI:
```bash
# View all SAQ keys
redis-cli keys "saq:*"

# View job details
redis-cli get "saq:job:default:{job_id}"

# View stats
redis-cli zrange "saq:default:stats" 0 -1 WITHSCORES
```

## Error Handling

SAQ errors are handled through:
1. Built-in error responses
2. Custom error logging
3. Task retry mechanisms

Example error handling:
```python
try:
    await queue.enqueue("ping", correlation_id=correlation_id)
except Exception as e:
    logging.error(f"Failed to enqueue task: {str(e)}")
    raise HTTPException(status_code=500, detail="Failed to process task")
```

## Running Workers

Start the SAQ worker using the provided wrapper:
```bash
python saq_worker.py
```

Or directly using SAQ CLI:
```bash
python -m saq app.worker.saq.settings --web --port 8081
``` 