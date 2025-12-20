#!/usr/bin/env python3
"""
Run the FastAPI Web Application
"""
import uvicorn
import os


def main():
    host = os.environ.get("WEBAPP_HOST", "0.0.0.0")
    port = int(os.environ.get("WEBAPP_PORT", 8000))
    reload = os.environ.get("WEBAPP_RELOAD", "false").lower() == "true"
    
    print(f"Starting Trading Bot Web App on http://{host}:{port}")
    print("Press Ctrl+C to stop")
    
    uvicorn.run(
        "webapp.app:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()
