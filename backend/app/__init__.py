# app/__init__.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from .api import setup_routes
from .utils.config_utils import get_config, save_example_env_file

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application
    """
    # Get application configuration
    config = get_config()
    
    # Create an example .env file if it doesn't exist
    if not os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.example")):
        save_example_env_file(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.example"))
    
    # Create FastAPI app
    app = FastAPI(title="NeonChat API", description="API for NeonChat application")
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    
    # Set up static files serving
    BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
    FRONTEND_BUILD_DIR = os.path.join(PROJECT_ROOT, "frontend", "dist")  # Primary location
    
    if not os.path.isdir(FRONTEND_BUILD_DIR):
        fallback_path = os.path.join(PROJECT_ROOT, "frontend", "static")
        if os.path.isdir(fallback_path):
            FRONTEND_BUILD_DIR = fallback_path
            print(f"INFO: Using frontend source directory: {FRONTEND_BUILD_DIR}")
        else:
            print(f"ERROR: Frontend directory not found")
            FRONTEND_BUILD_DIR = None
    
    if FRONTEND_BUILD_DIR:
        app.mount("/static_assets", StaticFiles(directory=FRONTEND_BUILD_DIR), name="static_assets")
    
    # Set up API routes
    setup_routes(app)
    
    @app.on_event("startup")
    async def startup_event():
        """
        Actions to perform on application startup.
        """
        print("Starting NeonChat API...")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """
        Actions to perform on application shutdown.
        """
        print("Shutting down NeonChat API...")
        
        # Clean up any resources (e.g., close database connections)
    
    return app
