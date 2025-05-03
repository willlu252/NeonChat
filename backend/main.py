# backend/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from typing import Dict, List, Any
from datetime import datetime
import uuid
from api_calls import execute_openai_call
from config_utils import get_config, save_example_env_file

# Get application configuration
config = get_config()

# Create an example .env file if it doesn't exist
if not os.path.exists(os.path.join(os.path.dirname(__file__), ".env.example")):
    save_example_env_file(os.path.join(os.path.dirname(__file__), ".env.example"))

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

active_connections: Dict[str, WebSocket] = {}
client_message_history: Dict[str, List[Dict[str, Any]]] = {}

# --- Path Configuration ---
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
FRONTEND_BUILD_DIR = os.path.join(PROJECT_ROOT, "frontend", "dist") # Primary location
if not os.path.isdir(FRONTEND_BUILD_DIR):
    fallback_path = os.path.join(PROJECT_ROOT, "frontend", "static")
    if os.path.isdir(fallback_path):
        FRONTEND_BUILD_DIR = fallback_path
        print(f"INFO: Using frontend source directory: {FRONTEND_BUILD_DIR}")
    else:
        print(f"ERROR: Frontend directory not found at primary '{os.path.join(PROJECT_ROOT, 'frontend', 'dist')}' or fallback '{fallback_path}'")
        FRONTEND_BUILD_DIR = None

# --- Serve Frontend index.html and Static Files ---
if FRONTEND_BUILD_DIR:
    # Mount the entire build directory to serve static files correctly relative to index.html
    app.mount("/static_assets", StaticFiles(directory=FRONTEND_BUILD_DIR), name="static_assets")

    @app.get("/{full_path:path}")
    async def serve_frontend_catch_all(request: Request, full_path: str):
        index_path = os.path.join(FRONTEND_BUILD_DIR, "index.html")
        # Check if requested path looks like a file or directory within the frontend dir
        requested_path = os.path.join(FRONTEND_BUILD_DIR, full_path)

        # If it's not a real file/dir or it's the base path, serve index.html (for SPA routing)
        if not os.path.exists(requested_path) or not os.path.isfile(requested_path) or full_path == "":
             if os.path.exists(index_path):
                 print(f"Serving index.html for path: /{full_path}")
                 return FileResponse(index_path)
             else:
                 return JSONResponse(status_code=404, content={"detail": "index.html not found"})
        else:
             # If it is a real file, let StaticFiles handle it (should be caught by mount first usually)
             # But as a fallback we can serve it directly - though mount is preferred.
             print(f"Serving specific file: /{full_path}")
             return FileResponse(requested_path)

else:
    @app.get("/")
    async def root_api_only():
        return {"message": "Backend running, but frontend directory not found."}


# --- WebSocket Endpoint ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_id = str(uuid.uuid4()); active_connections[client_id] = websocket; client_message_history[client_id] = []
    print(f"WS connected: {client_id}")
    try:
        await websocket.send_json({'role': 'system', 'content': client_id, 'type': 'client_id'})
        while True:
            data = await websocket.receive_json()
            if data.get('type') in ['text', 'image', 'file']:
                 message_type = data.get('type')
                 
                 # Create user message based on type
                 if message_type == 'text':
                     user_message = {'role': 'user', 'content': data['content'], 'type': 'text', 'timestamp': datetime.now().isoformat()}
                 elif message_type == 'image':  # image type
                     user_message = {
                         'role': 'user', 
                         'content': data['content'], 
                         'type': 'image', 
                         'timestamp': datetime.now().isoformat()
                     }
                     # Add caption if provided
                     if 'caption' in data:
                         user_message['caption'] = data['caption']
                 elif message_type == 'file':  # file type (non-image)
                     user_message = {
                         'role': 'user',
                         'content': data['content'],
                         'type': 'file',
                         'filename': data.get('filename', 'unnamed_file'),
                         'filetype': data.get('filetype', 'unknown'),
                         'filesize': data.get('filesize', 0),
                         'timestamp': datetime.now().isoformat()
                     }
                     # Add caption if provided
                     if 'caption' in data:
                         user_message['caption'] = data['caption']
                 
                 # Initialize message history if needed
                 if client_id not in client_message_history: 
                     client_message_history[client_id] = []
                 
                 # Add message to history
                 client_message_history[client_id].append(user_message)
                 
                 # Optional typing indicator
                 # await websocket.send_json({'role': 'system', 'content': 'typing', 'type': 'indicator'})
                 
                 # Get model ID
                 default_model = config["models"]["default"]
                 model_id = data.get('model_id', default_model)  # Model from client or default from config
                 print(f"Using model: {model_id} for {client_id} with message type: {message_type}")
                 
                 # Process with API
                 if message_type == 'text':
                     response = await execute_openai_call(model_id, client_message_history[client_id], data['content'])
                 else:  # image or file type
                     response = await execute_openai_call(model_id, client_message_history[client_id], data)
                 
                 # Add timestamp and send response
                 response['timestamp'] = datetime.now().isoformat()
                 client_message_history[client_id].append(response)
                 await websocket.send_json(response)
            else:
                 print(f"Ignoring message with invalid type or missing content: {data.get('type')}")
    except WebSocketDisconnect: print(f"WS disconnected: {client_id}")
    except Exception as e: print(f"WS error for {client_id}: {str(e)}")
    finally: # Cleanup
        if client_id in active_connections: del active_connections[client_id]
        if client_id in client_message_history: del client_message_history[client_id]

if __name__ == "__main__":
    if FRONTEND_BUILD_DIR: print(f"Attempting to serve frontend from: {FRONTEND_BUILD_DIR}")
    else: print("WARNING: Frontend directory not found.")
    
    # Get server configuration from config
    host = config["server"]["host"]
    port = config["server"]["port"]
    debug = config["server"]["debug"]
    
    print(f"Starting server on {host}:{port} (debug: {debug})")
    uvicorn.run("main:app", host=host, port=port, reload=debug)
