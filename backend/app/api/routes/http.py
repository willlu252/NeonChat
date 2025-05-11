# app/api/routes/http.py
from fastapi import APIRouter, Request, Response
from fastapi.responses import FileResponse, JSONResponse
import os
from typing import Dict, Any

# Create the router
router = APIRouter()

# Get application paths
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
FRONTEND_BUILD_DIR = os.path.join(PROJECT_ROOT, "frontend", "dist")  # Primary location

# Check if frontend build directory exists or use fallback
if not os.path.isdir(FRONTEND_BUILD_DIR):
    fallback_path = os.path.join(PROJECT_ROOT, "frontend", "static")
    if os.path.isdir(fallback_path):
        FRONTEND_BUILD_DIR = fallback_path
        print(f"INFO: Using frontend source directory: {FRONTEND_BUILD_DIR}")
    else:
        print(f"ERROR: Frontend directory not found at primary '{os.path.join(PROJECT_ROOT, 'frontend', 'dist')}' or fallback '{fallback_path}'")
        FRONTEND_BUILD_DIR = None

@router.get("/api/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "ok", "message": "API is running"}

@router.get("/api/config")
async def get_config():
    """Get application configuration"""
    from ...utils.config_utils import get_config
    
    # Get configuration but mask API keys
    config = get_config()
    for provider, key in config["api_keys"].items():
        if key:
            config["api_keys"][provider] = f"{key[:5]}...{key[-5:]}" if len(key) > 10 else "***"
        else:
            config["api_keys"][provider] = "Not set"
    
    return config

@router.get("/{full_path:path}")
async def serve_frontend_catch_all(request: Request, full_path: str):
    """
    Catch-all route to serve the frontend SPA
    
    Args:
        request: The incoming request
        full_path: The requested path
    """
    if not FRONTEND_BUILD_DIR:
        return JSONResponse(
            status_code=404, 
            content={"detail": "Frontend directory not found"}
        )
    
    index_path = os.path.join(FRONTEND_BUILD_DIR, "index.html")
    
    # Check if requested path looks like a file or directory within the frontend dir
    requested_path = os.path.join(FRONTEND_BUILD_DIR, full_path)
    
    # If it's not a real file/dir or it's the base path, serve index.html (for SPA routing)
    if not os.path.exists(requested_path) or not os.path.isfile(requested_path) or full_path == "":
        if os.path.exists(index_path):
            print(f"Serving index.html for path: /{full_path}")
            return FileResponse(index_path)
        else:
            return JSONResponse(
                status_code=404, 
                content={"detail": "index.html not found"}
            )
    else:
        # If it is a real file, serve it directly
        print(f"Serving specific file: /{full_path}")
        return FileResponse(requested_path)
