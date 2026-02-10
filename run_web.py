#!/usr/bin/env python3
"""Convenience script to run the web dashboard."""

import uvicorn
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


if __name__ == "__main__":
    print("Starting Facebook Ads Manager Web Dashboard...")
    print("Dashboard will be available at: http://localhost:8000")
    print("API documentation available at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server\n")

    uvicorn.run(
        "src.web.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
