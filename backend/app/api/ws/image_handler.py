# app/api/ws/image_handler.py
from fastapi import WebSocket
from typing import Dict, Any

from ...services.message_service import message_service
from ...services.api_service import api_service

async def handle_image_message(websocket: WebSocket, client_id: str, data: Dict[str, Any]):
    """
    Handle image messages sent via WebSocket.
    
    Args:
        websocket: The WebSocket connection
        client_id: The client's unique identifier
        data: The message data containing the image URL
    """
    # Create user message with image
    user_message = {
        'role': 'user', 
        'content': data['content'], 
        'type': 'image', 
        'timestamp': data.get('timestamp')
    }
    
    # Add caption if provided
    if 'caption' in data:
        user_message['caption'] = data['caption']
    
    # Add message to history
    message_service.add_message(client_id, user_message)
    
    # Get message history
    message_history = message_service.get_message_history(client_id)
    
    # Process with Claude API
    response = await api_service.execute_claude_call(message_history[:-1], data)
    
    # Add assistant message to history
    if response.get("type") != "error":
        message_service.add_message(client_id, response)
    
    # Send response to client
    await websocket.send_json(response)