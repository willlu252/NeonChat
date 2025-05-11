# backend/main.py - Entry point for the NeonChat API
import uvicorn
import os
from app import create_app

# Create the FastAPI application using our app factory
app = create_app()

if __name__ == "__main__":
    # Get host and port from environment variables or use defaults
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    debug = os.environ.get("DEBUG", "False").lower() in ("true", "1", "t")
    
    print(f"Starting NeonChat API on {host}:{port}")
    
    # Run the application with uvicorn
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug
    )
