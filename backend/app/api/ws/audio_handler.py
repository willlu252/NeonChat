# app/api/ws/audio_handler.py
from fastapi import WebSocket
from typing import Dict, Any

from ...services.message_service import message_service
from ...services.api_service import api_service
from ...services.voice_service import voice_service

async def handle_audio_message(websocket: WebSocket, client_id: str, data: Dict[str, Any]):
    """
    Handle audio messages sent via WebSocket.
    
    Args:
        websocket: The WebSocket connection
        client_id: The client's unique identifier
        data: The message data containing the audio content
    """
    # Check if conversational mode is enabled
    if data.get('conversational_mode', False):
        await handle_conversational_audio(websocket, client_id, data)
    else:
        await handle_basic_audio(websocket, client_id, data)

async def handle_basic_audio(websocket: WebSocket, client_id: str, data: Dict[str, Any]):
    """
    Handle basic audio transcription and response.
    
    Args:
        websocket: The WebSocket connection
        client_id: The client's unique identifier
        data: The message data containing the audio content
    """
    # Get audio data
    audio_data = data.get('audio_data', '')
    
    # First transcribe the audio to get the user's message
    transcription_result = await voice_service.speech_to_text(audio_data)
    
    if 'error' in transcription_result:
        # If transcription failed, send an error message
        await websocket.send_json({
            'role': 'system',
            'content': f"Transcription failed: {transcription_result['error']}",
            'type': 'error'
        })
        return
    
    # Create user message with transcribed text
    transcribed_text = transcription_result['text']
    user_message = message_service.create_user_message(
        transcribed_text,
        message_type='audio',
        audio_data=audio_data
    )
    
    # Add message to history
    message_service.add_message(client_id, user_message)
    
    # Send a confirmation with the transcribed text
    await websocket.send_json({
        'role': 'system',
        'content': f"Transcribed: {transcribed_text}",
        'type': 'transcription'
    })
    
    # Get model ID from data or use default
    model_id = data.get('model_id')
    message_history = message_service.get_message_history(client_id)
    
    # Process with API
    response = await api_service.execute_openai_call(model_id, message_history, transcribed_text)
    
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

async def handle_conversational_audio(websocket: WebSocket, client_id: str, data: Dict[str, Any]):
    """
    Handle conversational audio with direct voice-to-voice response.
    
    Args:
        websocket: The WebSocket connection
        client_id: The client's unique identifier
        data: The message data
    """
    # Get audio data and conversation mode
    audio_data = data.get('audio_data', '')
    conversation_mode = data.get('conversation_mode', 'cheap')
    
    # First transcribe the audio to get the user's message
    transcription_result = await voice_service.speech_to_text(audio_data)
    
    if 'error' in transcription_result:
        # If transcription failed, send an error message
        await websocket.send_json({
            'role': 'system',
            'content': f"Transcription failed: {transcription_result['error']}",
            'type': 'error'
        })
        return
    
    # Create user message with transcribed text
    transcribed_text = transcription_result['text']
    user_message = message_service.create_user_message(
        transcribed_text,
        message_type='audio',
        audio_data=audio_data
    )
    
    # Add message to history
    message_service.add_message(client_id, user_message)
    
    # Send a confirmation with the transcribed text
    await websocket.send_json({
        'role': 'system',
        'content': f"Transcribed: {transcribed_text}",
        'type': 'transcription'
    })
    
    # Get model ID from data or use default
    model_id = data.get('model_id')
    message_history = message_service.get_message_history(client_id)
    
    # Process with API
    response = await api_service.execute_openai_call(model_id, message_history, transcribed_text)
    
    # Add assistant message to history
    message_service.add_message(client_id, response)
    
    # Convert the response to speech
    voice = data.get('voice', 'alloy')
    speed = float(data.get('speed', 1.0))
    tts_response = await voice_service.text_to_speech(
        response['content'],
        voice=voice,
        speed=speed
    )
    
    if 'error' in tts_response:
        # If TTS failed, send text response only
        await websocket.send_json(response)
    else:
        # Send audio response
        audio_response = {
            'role': 'assistant',
            'content': response['content'],
            'audio_data': tts_response.get('audio_data', ''),
            'audio_format': tts_response.get('format', 'mp3'),
            'type': 'audio_response'
        }
        await websocket.send_json(audio_response)
