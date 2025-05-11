# app/api/ws/image_handler.py
from fastapi import WebSocket
from typing import Dict, Any

from ...services.message_service import message_service
from ...services.api_service import api_service
from ...services.voice_service import voice_service
from ...services.image_service import image_service

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
    
    # Get model ID from data or use default
    model_id = data.get('model_id')
    message_history = message_service.get_message_history(client_id)
    
    # Process with API
    response = await api_service.execute_openai_call(model_id, message_history, data)
    
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

async def handle_image_generation(websocket: WebSocket, client_id: str, data: Dict[str, Any]):
    """
    Handle image generation requests sent via WebSocket.
    
    Args:
        websocket: The WebSocket connection
        client_id: The client's unique identifier
        data: The message data containing the generation prompt
    """
    try:
        # Extract image generation parameters
        prompt = data.get('prompt', '')
        size = data.get('size', '1024x1024')
        quality = data.get('quality', 'standard')
        style = data.get('style', 'vivid')
        
        # Send an acknowledgement that the request is being processed
        await websocket.send_json({
            'role': 'system',
            'content': 'Generating image...',
            'type': 'status',
            'status': 'generating'
        })
        
        # Generate the image
        result = await image_service.generate_image(prompt, size, quality, style)
        
        if 'error' in result:
            # If there was an error, send it to the client
            await websocket.send_json({
                'role': 'system',
                'content': f"Image generation failed: {result['error']}",
                'type': 'error'
            })
        else:
            # If successful, send the generated image
            response = {
                'role': 'assistant',
                'content': result.get('revised_prompt', prompt),
                'type': 'image',
                'image_url': result['url'],
                'original_prompt': prompt
            }
            
            # Add the response to the message history
            message_service.add_message(client_id, response)
            
            # Send the response to the client
            await websocket.send_json(response)
    
    except Exception as e:
        # Handle any errors
        print(f"Error generating image: {str(e)}")
        await websocket.send_json({
            'role': 'system',
            'content': f"Error generating image: {str(e)}",
            'type': 'error'
        })
