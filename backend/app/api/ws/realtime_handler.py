# app/api/ws/realtime_handler.py
from fastapi import WebSocket
from typing import Dict, Any
import asyncio

from ...services.message_service import message_service
from ...services.voice_service import voice_service

# Dictionary to store realtime sessions
realtime_sessions = {}

async def handle_realtime_message(websocket: WebSocket, client_id: str, data: Dict[str, Any]):
    """
    Handle realtime audio messages sent via WebSocket.
    
    Args:
        websocket: The WebSocket connection
        client_id: The client's unique identifier
        data: The message data
    """
    message_type = data.get('type')
    
    if message_type == 'realtime_start':
        await handle_realtime_start(websocket, client_id, data)
    elif message_type == 'realtime_stop':
        await handle_realtime_stop(websocket, client_id, data)
    elif message_type == 'realtime_audio':
        await handle_realtime_audio(websocket, client_id, data)
    else:
        await websocket.send_json({
            'role': 'system',
            'content': f"Unknown realtime message type: {message_type}",
            'type': 'error'
        })

async def handle_realtime_start(websocket: WebSocket, client_id: str, data: Dict[str, Any]):
    """
    Start a realtime audio conversation session.
    
    Args:
        websocket: The WebSocket connection
        client_id: The client's unique identifier
        data: The message data
    """
    # Check if a session is already active for this client
    if client_id in realtime_sessions:
        # Stop existing session
        await handle_realtime_stop(websocket, client_id, data)
    
    # Get conversation mode
    conversation_mode = data.get('conversation_mode', 'cheap')
    
    # Send confirmation to client
    await websocket.send_json({
        'role': 'system',
        'content': 'Starting realtime audio session...',
        'type': 'realtime_status',
        'status': 'starting'
    })
    
    # Create a callback to handle responses
    async def realtime_callback(event_data):
        try:
            # Forward the event to the client
            await websocket.send_json(event_data)
        except Exception as e:
            print(f"Error in realtime callback: {str(e)}")
    
    try:
        # Store session information
        realtime_sessions[client_id] = {
            'websocket': websocket,
            'mode': conversation_mode,
            'callback': realtime_callback,
            'active': True
        }
        
        # Notify client that session is ready
        await websocket.send_json({
            'role': 'system',
            'content': 'Realtime audio session started',
            'type': 'realtime_status',
            'status': 'started',
            'mode': conversation_mode
        })
    
    except Exception as e:
        # Handle any errors during session setup
        print(f"Error starting realtime session: {str(e)}")
        if client_id in realtime_sessions:
            del realtime_sessions[client_id]
        
        await websocket.send_json({
            'role': 'system',
            'content': f"Error starting realtime session: {str(e)}",
            'type': 'error'
        })

async def handle_realtime_stop(websocket: WebSocket, client_id: str, data: Dict[str, Any]):
    """
    Stop a realtime audio conversation session.
    
    Args:
        websocket: The WebSocket connection
        client_id: The client's unique identifier
        data: The message data
    """
    if client_id in realtime_sessions:
        # Mark session as inactive
        realtime_sessions[client_id]['active'] = False
        
        # Clean up any resources
        del realtime_sessions[client_id]
        
        # Notify client
        await websocket.send_json({
            'role': 'system',
            'content': 'Realtime audio session stopped',
            'type': 'realtime_status',
            'status': 'stopped'
        })
    else:
        await websocket.send_json({
            'role': 'system',
            'content': 'No active realtime session to stop',
            'type': 'realtime_status',
            'status': 'no_session'
        })

async def handle_realtime_audio(websocket: WebSocket, client_id: str, data: Dict[str, Any]):
    """
    Process audio data for a realtime conversation.
    
    Args:
        websocket: The WebSocket connection
        client_id: The client's unique identifier
        data: The message data containing audio chunks
    """
    if client_id not in realtime_sessions or not realtime_sessions[client_id]['active']:
        # No active session
        await websocket.send_json({
            'role': 'system',
            'content': 'No active realtime session',
            'type': 'error'
        })
        return
    
    # Get audio data
    audio_data = data.get('audio_data', '')
    
    try:
        # Process the audio data for transcription
        # This would typically send to a streaming transcription service
        # For now, we'll use the basic transcription
        
        # Notify client that we received audio
        await websocket.send_json({
            'role': 'system',
            'content': 'Processing audio chunk...',
            'type': 'realtime_status',
            'status': 'processing'
        })
        
        # Simple implementation - transcribe the audio
        transcription_result = await voice_service.speech_to_text(audio_data)
        
        if 'error' in transcription_result:
            # If transcription failed, send an error message
            await websocket.send_json({
                'role': 'system',
                'content': f"Transcription failed: {transcription_result['error']}",
                'type': 'error'
            })
            return
        
        # Send transcription result
        await websocket.send_json({
            'role': 'system',
            'content': transcription_result['text'],
            'type': 'transcription',
            'is_realtime': True
        })
        
        # For now, we'll send a simple echo response
        # In a full implementation, this would connect to a realtime 
        # conversation service with proper streaming
        response_text = f"I heard: {transcription_result['text']}"
        
        # Generate TTS response
        tts_response = await voice_service.text_to_speech(
            response_text,
            voice=data.get('voice', 'alloy'),
            speed=float(data.get('speed', 1.0))
        )
        
        if 'error' in tts_response:
            # If TTS failed, send text response only
            await websocket.send_json({
                'role': 'assistant',
                'content': response_text,
                'type': 'text',
                'is_realtime': True
            })
        else:
            # Send audio response
            await websocket.send_json({
                'role': 'assistant',
                'content': response_text,
                'audio_data': tts_response.get('audio_data', ''),
                'audio_format': tts_response.get('format', 'mp3'),
                'type': 'audio_response',
                'is_realtime': True
            })
        
    except Exception as e:
        # Handle errors
        print(f"Error processing realtime audio: {str(e)}")
        await websocket.send_json({
            'role': 'system',
            'content': f"Error processing audio: {str(e)}",
            'type': 'error'
        })
