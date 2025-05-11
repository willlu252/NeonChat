# app/api/ws/file_handler.py
from fastapi import WebSocket
from typing import Dict, Any

from ...services.message_service import message_service
from ...services.api_service import api_service
from ...services.voice_service import voice_service
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
    
    # Process the file content
    success, file_text = process_file_content(data['content'], data.get('filetype', 'text/plain'))
    
    if not success:
        # If file processing failed, send an error message
        await websocket.send_json({
            'role': 'system',
            'content': file_text,  # This will contain the error message
            'type': 'error'
        })
        return
    
    # Prepare processed data for the API call
    processed_data = {
        'type': 'text',
        'content': f"File content: {file_text}",
    }
    if 'caption' in data:
        processed_data['content'] = f"{data['caption']}\n\n{processed_data['content']}"
    
    # Get model ID from data or use default
    model_id = data.get('model_id')
    message_history = message_service.get_message_history(client_id)
    
    # Process with API
    response = await api_service.execute_openai_call(model_id, message_history, processed_data)
    
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
