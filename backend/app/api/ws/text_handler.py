# app/api/ws/text_handler.py
from fastapi import WebSocket
from typing import Dict, Any
from datetime import datetime

from ...services.message_service import message_service
from ...services.api_service import api_service
from ...services.voice_service import voice_service

async def handle_text_message(websocket: WebSocket, client_id: str, data: Dict[str, Any]):
    """
    Handle text messages sent via WebSocket.
    
    Args:
        websocket: The WebSocket connection
        client_id: The client's unique identifier
        data: The message data
    """
    # Create user message
    user_message = message_service.create_user_message(data['content'])
    
    # Add message to history
    message_service.add_message(client_id, user_message)
    
    # Get model ID from data or use default
    model_id = data.get('model_id')  # Model from client or default from config
    message_history = message_service.get_message_history(client_id)
    
    # Process with API
    response = await api_service.execute_openai_call(model_id, message_history, data['content'])
    
    # Add assistant message to history
    message_service.add_message(client_id, response)
    
    # If TTS is enabled, convert the response to speech
    if data.get('tts_enabled', False):
        tts_response = await voice_service.text_to_speech(
            response['content'],
            voice=data.get('voice', 'alloy'),
            speed=float(data.get('speed', 1.0))
        )
        if 'error' not in tts_response:
            response['audio_data'] = tts_response.get('audio_data', '')
            response['audio_format'] = tts_response.get('format', 'mp3')
            response['type'] = 'audio_response'
    
    # Send response to client
    await websocket.send_json(response)
