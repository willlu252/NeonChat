# app/api/__init__.py
from fastapi import FastAPI
from .routes import api_router
from .routes.ws import websocket_endpoint

def setup_routes(app: FastAPI):
    """
    Set up all API routes and WebSocket endpoints.
    
    Args:
        app: FastAPI application instance
    """
    # Mount API router
    app.include_router(api_router)
    
    # Add WebSocket endpoint
    app.add_api_websocket_route("/ws", websocket_endpoint)
    
    return app
