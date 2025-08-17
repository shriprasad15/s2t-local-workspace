# FastStream Core Documentation

## Overview
The FastStream core module provides essential functionality for message processing and distributed tracing in the FastStream application framework. It implements correlation ID-based tracking and structured logging to help monitor and debug message flow through the system.

## Key Components

### MsgBaseModel
A base Pydantic model for all messages in the system. It includes:
- `correlation_id`: A unique identifier for tracking messages
- `data`: Generic payload field that can hold any type of data

### MessageStatus
An enumeration of possible message states in the system:
- `RECEIVED`: Initial state when message enters the system
- `PROCESSING`: Message is being processed
- `COMPLETED`: Processing finished successfully
- `FAILED`: Processing encountered an error
- `RETRYING`: System is attempting to retry processing
- `CANCELLED`: Processing was cancelled
- `PARTIALLY`: Message was partially processed

### Logging Decorator
The `@log_faststream` decorator provides automatic correlation ID tracking in logs:
- Extracts correlation ID from message objects
- Adds correlation ID prefix to all log messages
- Supports both synchronous and asynchronous functions
- Automatically restores original logging configuration after function execution

## Usage Example

```python
from core.faststream_core import MsgBaseModel, log_faststream

class UserMessage(MsgBaseModel[dict]):
    pass

@log_faststream
async def process_message(msg: UserMessage):
    logging.info("Processing user message")  # Will include correlation ID
    # Process message
    return result
```

## Best Practices
1. Always use MsgBaseModel as the base class for message types
2. Apply the @log_faststream decorator to message processing functions
3. Use correlation IDs for tracking related messages across services
4. Monitor message status transitions for system health