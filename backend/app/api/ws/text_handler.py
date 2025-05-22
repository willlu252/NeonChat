# app/api/ws/text_handler.py
from fastapi import WebSocket
from typing import Dict, Any
from datetime import datetime

from ...services.message_service import message_service
from ...services.api_service import api_service

async def handle_text_message(websocket: WebSocket, client_id: str, data: Dict[str, Any]):
    """
    Handle text messages sent via WebSocket with streaming response.
    
    Args:
        websocket: The WebSocket connection
        client_id: The client's unique identifier
        data: The message data
    """
    # Create user message
    user_message_content = data['content']
    user_message = message_service.create_user_message(user_message_content)
    
    # Add message to history
    message_service.add_message(client_id, user_message)
    
    # Get the full message history *after* adding the new user message
    full_message_history = message_service.get_message_history(client_id)
    
    current_user_input_structured = {}
    if full_message_history:
        current_user_input_structured = full_message_history[-1]
    
    history_for_claude = []
    if len(full_message_history) > 1:
        history_for_claude = full_message_history[:-1]

    # Process with Claude API using streaming
    full_response_content = ""
    first_chunk = True
    
    async for chunk in api_service.execute_claude_call_streaming(
        history_for_claude, 
        current_user_input_structured 
    ):
        if chunk.get("type") == "text_chunk":
            # Send streaming chunk to frontend
            full_response_content += chunk.get("content", "")
            await websocket.send_json({
                "role": "assistant",
                "content": chunk.get("content", ""),
                "type": "text_chunk",
                "done": False
            })
            
        elif chunk.get("done") or chunk.get("type") == "error":
            # Send final message and add to history
            final_response = {
                "role": "assistant",
                "content": full_response_content if chunk.get("type") != "error" else chunk.get("content"),
                "model": chunk.get("model", "claude-3-7-sonnet-20250219"),
                "type": "text" if chunk.get("type") != "error" else "error",
                "done": True
            }
            
            # Add complete response to message history
            if chunk.get("type") != "error" and full_response_content:
                message_service.add_message(client_id, {
                    "role": "assistant",
                    "content": full_response_content,
                    "model": chunk.get("model", "claude-3-7-sonnet-20250219"),
                    "type": "text"
                })
            
            # Send final completion signal
            await websocket.send_json(final_response)
            break