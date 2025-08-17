# Development Guide

This guide provides instructions for developing and extending the FastAPI boilerplate.

## API Development

### API Versioning

The project uses path-based versioning (e.g., `/v1/`, `/v2/`). Each version has its own router in the `app/api/` directory:

```
app/api/
├── v1/
│   ├── __init__.py
│   └── ping.py
└── v2/
    ├── __init__.py
    └── ping.py
```

When creating new endpoints:
1. Choose the appropriate version directory
2. Create a new router file or add to existing one
3. Import and include the router in the version's `__init__.py`

Example router file:
```python
from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/endpoint")
async def endpoint(request: Request):
    return {"message": "New endpoint"}
```

### Adding New Features

When adding new features:

1. **API Endpoints**
   - Create endpoints in appropriate version directory
   - Use type hints for request/response models
   - Include docstrings for OpenAPI documentation
   - Add correlation ID tracking if needed

2. **FastStream Workers**
   - Create new worker files in `app/worker/faststream/`
   - Define message models using Pydantic
   - Implement message handlers with proper logging
   - Use the `@log_faststream` decorator

3. **Configuration**
   - Add new configuration options to `core/config.py`
   - Update environment variables in `.env`
   - Document configuration options

## Project Structure

### Adding New Components

When adding new components:

1. **Core Components** (`/core`)
   - Core functionality used across the application
   - Configuration, middleware, server setup
   - Base classes and utilities

2. **Application Components** (`/app`)
   - Business logic and API endpoints
   - Message handlers and workers
   - Domain-specific code

3. **Documentation** (`/docs`)
   - Add documentation for new features
   - Update existing documentation as needed
   - Include examples and usage guidelines

## Best Practices

### Code Style

Follow these guidelines:

1. **Type Hints**
   ```python
   from typing import Optional, List

   def process_items(items: List[str]) -> Optional[str]:
       if not items:
           return None
       return items[0]
   ```

2. **Docstrings**
   ```python
   def function_name(param: str) -> bool:
       """
       Brief description of function.

       Args:
           param: Description of parameter

       Returns:
           Description of return value
       """
       return True
   ```

3. **Error Handling**
   ```python
   from fastapi import HTTPException

   async def handle_request(request: Request):
       try:
           result = await process_request(request)
           return result
       except ValueError as e:
           raise HTTPException(status_code=400, detail=str(e))
       except Exception as e:
           raise HTTPException(status_code=500, detail="Internal server error")
   ```

### Logging

Use structured logging with correlation IDs:

```python
import logging
from core.middleware import correlation_id_ctx_var

logger = logging.getLogger(__name__)

def process_request():
    correlation_id = correlation_id_ctx_var.get()
    logger.info(
        "Processing request",
        extra={
            "correlation_id": correlation_id,
            "operation": "process_request"
        }
    )
```

### Testing

Write tests for new features:

1. **API Tests**
   ```python
   from fastapi.testclient import TestClient

   def test_endpoint(client: TestClient):
       response = client.get("/v1/endpoint")
       assert response.status_code == 200
       assert response.json() == {"message": "success"}
   ```

2. **Worker Tests**
   ```python
   import pytest
   from app.worker.faststream.handler import process_message

   @pytest.mark.asyncio
   async def test_process_message():
       message = {"key": "value"}
       result = await process_message(message)
       assert result.status == "completed"
   ```

## Docker Development

### Local Development with Docker

1. Build and run services:
   ```bash
   docker-compose up -d --build
   ```

2. View logs:
   ```bash
   docker-compose logs -f app
   ```

3. Rebuild specific service:
   ```bash
   docker-compose up -d --build app
   ```

### Debugging

#### Remote Debugging with VSCode

1. Build and run the debug container:
    ```bash
    docker build -f Dockerfile.debug -t app-debug .
    docker run -p 8000:8000 -p 5678:5678 app-debug
    ```

2. Add the following configuration to your `.vscode/launch.json`:
    ```json
    {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Python: Remote Attach",
                "type": "python",
                "request": "attach",
                "connect": {
                    "host": "localhost",
                    "port": 5678
                },
                "pathMappings": [
                    {
                        "localRoot": "${workspaceFolder}",
                        "remoteRoot": "/app"
                    }
                ]
            }
        ]
    }
    ```

3. Start debugging in VSCode:
   - Open the Run and Debug view (Ctrl+Shift+D)
   - Select "Python: Remote Attach" from the configuration dropdown
   - Click Start Debugging (F5)
   - The application will start once the debugger is attached

4. Container Shell Access:
    ```bash
    docker-compose exec app bash
    ```

5. View Logs:
    ```bash
    docker-compose logs -f app
    ```

6. Check Kafka topics:
    ```bash
    docker-compose exec kafka kafka-topics.sh --list --bootstrap-server localhost:9092