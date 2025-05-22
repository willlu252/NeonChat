# app/api/ws/file_handler.py
from fastapi import WebSocket
from typing import Dict, Any

from ...services.message_service import message_service
from ...services.api_service import api_service
from ...utils.file_utils import process_file_content

async def handle_file_message(websocket: WebSocket, client_id: str, data: Dict[str, Any]):
    """
    Handle file messages sent via WebSocket.
    
    Args:
        websocket: The WebSocket connection
        client_id: The client's unique identifier
        data: The message data containing the file content
    """
    # Create user message with file
    user_message = {
        'role': 'user',
        'content': data['content'],
        'type': 'file',
        'filename': data.get('filename', 'unnamed_file'),
        'filetype': data.get('filetype', 'unknown'),
        'filesize': data.get('filesize', 0),
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