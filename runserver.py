#!/usr/bin/env python3
"""
Server startup script for the LLM Code Deployment API.
Starts FastAPI backend on port 7860, compatible with Hugging Face Spaces Docker deployments.
"""

import uvicorn
from pathlib import Path

if __name__ == "__main__":
    # If your app needs to store temporary files or logs, ensure directories are created here.
    # Path("sandbox").mkdir(exist_ok=True)      # Optional: for generated apps/files
    # Path("logs").mkdir(exist_ok=True)         # Optional: for logging
    # Path("examples").mkdir(exist_ok=True)     # Optional: for usage examples

    # Start the FastAPI app; Hugging Face Spaces requires port 7860
    uvicorn.run(
        "app.main:app",        # Your FastAPI entrypoint (update path if needed)
        host="0.0.0.0",
        port=7860,
        reload=False,
        log_level="info"
    )
