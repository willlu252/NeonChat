# app/api/routes/ws.py
from fastapi import WebSocket, WebSocketDisconnect
import uuid
from typing import Dict, Any
from datetime import datetime

from ...services.message_service import message_service
from ..ws import text_handler, image_handler, file_handler

# Dictionary to store active WebSocket connections
active_connections = {}

async def websocket_endpoint(websocket: WebSocket):
    """
    Handle WebSocket connections and route messages to appropriate handlers.
    
    Args:
        websocket: The WebSocket connection
    """
    await websocket.accept()
    client_id = str(uuid.uuid4())
    active_connections[client_id] = websocket
    print(f"WS connected: {client_id}")
    
    try:
        # Send client ID to the client
        await websocket.send_json({'role': 'system', 'content': client_id, 'type': 'client_id'})
        
        while True:
            # Receive JSON data from the client
            data = await websocket.receive_json()
            message_type = data.get('type')
            
            # Route the message to the appropriate handler based on type
            if message_type == 'text':
                await text_handler.handle_text_message(websocket, client_id, data)
                
            elif message_type == 'image':
                await image_handler.handle_image_message(websocket, client_id, data)
                
            elif message_type == 'file':
                await file_handler.handle_file_message(websocket, client_id, data)
                
            elif message_type == 'generate_image':
                await image_handler.handle_image_generation(websocket, client_id, data)
                
            else:
                # Unknown message type
                await websocket.send_json({
                    'role': 'system',
                    'content': f"Unknown message type: {message_type}",
                    'type': 'error'
                })
    
    except WebSocketDisconnect:
        # Handle client disconnection
        print(f"WS disconnected: {client_id}")
        if client_id in active_connections:
            del active_connections[client_id]
    
    except Exception as e:
        # Handle other exceptions
        print(f"WS error for {client_id}: {str(e)}")
        try:
            await websocket.send_json({
                'role': 'system',
                'content': f"Error: {str(e)}",
                'type': 'error'
            })
        except:
            pass
        
        # Clean up connection if still active
        if client_id in active_connections:
            del active_connections[client_id]
