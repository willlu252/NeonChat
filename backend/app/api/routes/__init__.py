# app/api/routes/__init__.py
from fastapi import APIRouter
from . import http
from . import ws

api_router = APIRouter()

# Include HTTP routes
api_router.include_router(http.router)

# The WebSocket route will be mounted directly to the app in ../api/__init__.py
