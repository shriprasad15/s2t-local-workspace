import json
import logging.config
from pathlib import Path

import uvicorn

from core.config import settings
from core.log_config import get_log_config

logging.config.dictConfig(get_log_config())

# Keep this so we can run uvicorn main:app --host=0.0.0.0 --port=8000 --reload
from core.server import app

# Export OpenAPI schema to file
def export_openapi_schema():
    # Ensure docs directory exists
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    
    # Get OpenAPI schema
    openapi_schema = app.openapi()
    
    # Write to file
    openapi_path = docs_dir / "openapi.json"
    with open(openapi_path, "w") as f:
        json.dump(openapi_schema, f, indent=2)
    
    logging.info(f"OpenAPI schema exported to {openapi_path}")

# Export OpenAPI schema when app starts
export_openapi_schema()

if __name__ == "__main__":
    import os
    
    port = int(os.getenv("PORT", settings.APP_PORT))
    host = os.getenv("HOST", "0.0.0.0")
    
    logging.info(f"Starting ETL AI Agent server on {host}:{port}")
    
    uvicorn.run(
        app="core.server:app",
        host=host,
        port=port,
        reload=True if settings.ENVIRONMENT != "production" else False,
        log_config=get_log_config()
    )
