#!/usr/bin/env python3
"""
Simple script to run the CSV Chart Agent backend
"""

import os
import subprocess
import sys
from pathlib import Path

def install_dependencies():
    """Install Python dependencies"""
    print("🔧 Installing Python dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def run_backend():
    """Run the FastAPI backend"""
    print("🚀 Starting CSV Chart Agent Backend...")
    os.environ.setdefault("HOST", "0.0.0.0")
    os.environ.setdefault("PORT", "8000")
    
    # Import and run the app
    import uvicorn
    uvicorn.run(
        "backend:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )

if __name__ == "__main__":
    # Check if requirements.txt exists
    if not Path("requirements.txt").exists():
        print("❌ requirements.txt not found!")
        sys.exit(1)
    
    # Install dependencies if needed
    try:
        import pydantic_ai
        import fastapi
        import copilotkit
    except ImportError:
        install_dependencies()
    
    # Run the backend
    run_backend()