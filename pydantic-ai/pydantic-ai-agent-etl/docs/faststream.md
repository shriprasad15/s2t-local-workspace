# FastStream Integration Guide

This guide explains how FastStream is integrated into the FastAPI boilerplate for event-driven processing using Kafka.

## Overview

FastStream is used to handle asynchronous message processing with Kafka. The integration provides:
- Message publishing from API endpoints
- Message subscription and processing
- Correlation ID tracking across services
- Structured logging

## Configuration

FastStream configuration is managed through environment variables:

```env
FASTSTREAM_PROVIDER="localhost:9092"  # Kafka broker address
FASTSTREAM_ENABLE=true               # Enable/disable FastStream integration
```

## Message Models

Messages use Pydantic models for validation:

```python
# Base message model with correlation ID
class MsgBaseModel[T](BaseModel):
    correlation_id: str
    data: Optional[T] = None

# Example message content
class MessageContent(BaseModel):
    message: str
    timestamp: Optional[str] = None

# Request/Response models
class SampleReqMsg(MsgBaseModel[MessageContent]):
    data: Optional[MessageContent] = None

class SampleResMsg(MsgBaseModel[MessageContent]):
    data: Optional[MessageContent] = None
    status: MessageStatus = Field(default=MessageStatus.RECEIVED)
```

## Message Handlers

FastStream handlers are implemented using the `KafkaRouter`:

```python
from faststream.kafka import KafkaRouter

router = KafkaRouter()

@router.subscriber("in-topic")
@log_faststream
async def task_handler(body: SampleReqMsg, logger: Logger) -> SampleResMsg:
    logger.info("Logging from in-topic when receiving message")
    
    response = SampleResMsg(
        correlation_id=body.correlation_id,
        data=MessageContent(
            message="pong from subscriber",
            timestamp="2024-03-19T10:00:01Z"
        ),
        status=MessageStatus.COMPLETED
    )
    return response
```

## Publishing Messages

Messages can be published to Kafka topics from API endpoints:

```python
from core.faststream import publish_message

@router.get("/ping")
async def ping(request: Request):
    correlation_id = correlation_id_ctx_var.get()
    
    message = SampleReqMsg(
        correlation_id=correlation_id,
        data=MessageContent(
            message="Send for in-topic",
            timestamp="2024-03-19T10:00:01Z"
        )
    )
    
    await publish_message(request, message, "in-topic")
    return {"version": settings.APP_VERSION, "message": "pong"}
```

## Correlation ID

The correlation ID is automatically:
1. Generated for each incoming HTTP request
2. Added to the context using ContextVar
3. Included in all published messages
4. Logged with all log messages

This enables request tracking across the entire system.

## Logging

FastStream operations are automatically logged with:
- Correlation ID
- Message content
- Operation status
- Timestamps

Example log output:
```json
{
    "timestamp": "2024-01-12T19:17:45+08:00",
    "correlation_id": "123e4567-e89b-12d3-a456-426614174000",
    "level": "INFO",
    "message": "Logging from in-topic when receiving message",
    "topic": "in-topic",
    "operation": "subscribe"
}
```

## Error Handling

FastStream errors are handled through:
1. Built-in error responses
2. Custom error logging
3. Error status in response messages

Example error handling:
```python
try:
    await publish_message(request, message, "in-topic")
except Exception as e:
    logger.error(f"Failed to publish message: {str(e)}")
    raise HTTPException(status_code=500, detail="Failed to process message")
```

## Testing

To test FastStream functionality:

1. Ensure Kafka is running:
```bash
docker-compose up -d kafka
```

2. Send a request to the ping endpoint:
```bash
curl http://localhost:8000/v1/ping
```

3. Check the logs to see the message flow:
```bash
docker-compose logs -f app
