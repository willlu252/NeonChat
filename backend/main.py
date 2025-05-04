# backend/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import base64
from typing import Dict, List, Any
from datetime import datetime
import uuid
from api_calls import execute_openai_call, generate_image, text_to_speech, speech_to_text
from realtime_api import realtime_manager, transcribe_audio, FFMPEG_PATH
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
            if data.get('type') in ['text', 'image', 'file', 'audio', 'generate_image', 'realtime_audio', 'realtime_start', 'realtime_stop']:
                message_type = data.get('type')
                
                # Initialize message history if needed
                if client_id not in client_message_history: 
                    client_message_history[client_id] = []
                
                # Get model ID
                default_model = config["models"]["default"]
                model_id = data.get('model_id', default_model)  # Model from client or default from config
                print(f"Using model: {model_id} for {client_id} with message type: {message_type}")
                
                # Create user message based on type
                if message_type == 'text':
                    user_message = {'role': 'user', 'content': data['content'], 'type': 'text', 'timestamp': datetime.now().isoformat()}
                    
                    # Add message to history
                    client_message_history[client_id].append(user_message)
                    
                    # Process with API
                    response = await execute_openai_call(model_id, client_message_history[client_id], data['content'])
                    
                    # If TTS is enabled, convert the response to speech
                    if data.get('tts_enabled', False):
                        tts_response = await text_to_speech(
                            response['content'],
                            voice=data.get('voice', 'alloy'),
                            speed=float(data.get('speed', 1.0))
                        )
                        if 'error' not in tts_response:
                            response['audio_data'] = tts_response.get('audio_data', '')
                            response['audio_format'] = tts_response.get('format', 'mp3')
                            response['type'] = 'audio_response'
                
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
                    
                    # Add message to history
                    client_message_history[client_id].append(user_message)
                    
                    # Process with API
                    response = await execute_openai_call(model_id, client_message_history[client_id], data)
                    
                    # If TTS is enabled, convert the response to speech
                    if data.get('tts_enabled', False):
                        tts_response = await text_to_speech(
                            response['content'],
                            voice=data.get('voice', 'alloy'),
                            speed=float(data.get('speed', 1.0))
                        )
                        if 'error' not in tts_response:
                            response['audio_data'] = tts_response.get('audio_data', '')
                            response['audio_format'] = tts_response.get('format', 'mp3')
                            response['type'] = 'audio_response'
                
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
                    
                    # Add message to history
                    client_message_history[client_id].append(user_message)
                    
                    # Process with API
                    response = await execute_openai_call(model_id, client_message_history[client_id], data)
                    
                    # If TTS is enabled, convert the response to speech
                    if data.get('tts_enabled', False):
                        tts_response = await text_to_speech(
                            response['content'],
                            voice=data.get('voice', 'alloy'),
                            speed=float(data.get('speed', 1.0))
                        )
                        if 'error' not in tts_response:
                            response['audio_data'] = tts_response.get('audio_data', '')
                            response['audio_format'] = tts_response.get('format', 'mp3')
                            response['type'] = 'audio_response'
                
                elif message_type == 'audio':  # audio recording
                    # Check if conversational mode is enabled
                    if data.get('conversational_mode', False):
                        # Get conversation mode (cheap or complex)
                        conversation_mode = data.get('conversation_mode', 'cheap')
                        print(f"DEBUG: Received audio message with conversational_mode=True, conversation_mode={conversation_mode}")
                        
                        # Get audio data
                        audio_data = data.get('audio_data', '')
                        audio_data_length = len(audio_data) if audio_data else 0
                        print(f"DEBUG: Audio data received, length: {audio_data_length}")
                        
                        # First transcribe the audio to get the user's message
                        print(f"DEBUG: Transcribing audio for client {client_id}...")
                        transcription_result = await speech_to_text(audio_data)
                        
                        if 'error' in transcription_result:
                            print(f"ERROR: Transcription failed: {transcription_result['error']}")
                            voice_response = {'error': transcription_result['error']}
                        else:
                            print(f"DEBUG: Transcription successful: '{transcription_result['text']}'")
                            
                            # Create user message with transcribed text
                            user_message = {
                                'role': 'user',
                                'content': transcription_result['text'],
                                'type': 'text',
                                'original_type': 'audio',
                                'timestamp': datetime.now().isoformat()
                            }
                            
                            # Add to message history
                            client_message_history[client_id].append(user_message)
                            
                            # Define a new realtime callback function for each session
                            async def realtime_callback(session_id, event):
                                try:
                                    event_type = event.get('type', 'unknown')
                                    print(f"DEBUG: Realtime callback received event type: {event_type}")
                                    
                                    if event_type == 'text_delta':
                                        # Send text delta to the client
                                        delta = event.get('delta', '')
                                        print(f"DEBUG: Text delta: '{delta}'")
                                        await websocket.send_json({
                                            'role': 'assistant',
                                            'content': delta,
                                            'type': 'text_delta',
                                            'timestamp': datetime.now().isoformat()
                                        })
                                    elif event_type == 'audio_delta':
                                        # Send audio delta to the client
                                        delta_size = len(event.get('delta', b''))
                                        print(f"DEBUG: Audio delta received, size: {delta_size} bytes")
                                        await websocket.send_json({
                                            'role': 'assistant',
                                            'audio_data': base64.b64encode(event.get('delta', b'')).decode('utf-8'),
                                            'type': 'audio_delta',
                                            'timestamp': datetime.now().isoformat()
                                        })
                                    elif event_type == 'response_done':
                                        # Send a message indicating the response is complete
                                        print(f"DEBUG: Response complete event received")
                                        await websocket.send_json({
                                            'role': 'system',
                                            'content': 'Response complete',
                                            'type': 'response_done',
                                            'timestamp': datetime.now().isoformat()
                                        })
                                    elif event_type == 'error':
                                        print(f"ERROR: Realtime API error: {event.get('error', 'unknown error')}")
                                except Exception as e:
                                    print(f"ERROR: Exception in realtime callback: {str(e)}")
                                    import traceback
                                    print(f"ERROR TRACEBACK: {traceback.format_exc()}")
                            
                            # Store the callback function on the websocket object
                            websocket.realtime_callback = realtime_callback
                            
                            # Check if a session already exists for this client
                            session_exists = client_id in realtime_manager.sessions
                            
                            if not session_exists:
                                # Create a new realtime session
                                print(f"DEBUG: Creating new realtime session for client {client_id} with mode {conversation_mode}...")
                                await realtime_manager.create_session(client_id, websocket.realtime_callback, conversation_mode)
                            else:
                                print(f"DEBUG: Using existing realtime session for client {client_id}")
                            
                            # Send the audio data to the session
                            print(f"DEBUG: Sending audio data to realtime session for client {client_id}...")
                            await realtime_manager.send_audio(client_id, audio_data)
                            
                            # Force enable voice responses for realtime sessions
                            print(f"DEBUG: Forcing voice responses for realtime session {client_id}")
                            data['tts_enabled'] = True
                            
                            # Send a message to the client with the transcription immediately
                            await websocket.send_json({
                                'role': 'system',
                                'content': f"Transcription: {transcription_result['text']}",
                                'type': 'transcription',
                                'timestamp': datetime.now().isoformat()
                            })
                            
                            # Also send a user message to display in the chat
                            await websocket.send_json({
                                'role': 'user',
                                'content': transcription_result['text'],
                                'type': 'text',
                                'timestamp': datetime.now().isoformat()
                            })
                            
                            # No immediate response needed, as the realtime session will send events
                            continue
                        
                        if 'error' in voice_response:
                            response = {
                                'role': 'system',
                                'content': f"Error in voice conversation: {voice_response['error']}",
                                'type': 'text',
                                'timestamp': datetime.now().isoformat()
                            }
                        else:
                            # First transcribe the audio to get the user's message
                            transcription_result = await speech_to_text(data.get('audio_data', ''))
                            
                            if 'error' not in transcription_result:
                                # Create user message with transcribed text
                                user_message = {
                                    'role': 'user',
                                    'content': transcription_result['text'],
                                    'type': 'text',
                                    'original_type': 'audio',
                                    'timestamp': datetime.now().isoformat()
                                }
                                
                                # Add to message history
                                client_message_history[client_id].append(user_message)
                            
                            # Create response with text and audio
                            response = {
                                'role': 'assistant',
                                'content': voice_response['text'],
                                'audio_data': voice_response['audio_data'],
                                'audio_format': voice_response['format'],
                                'type': 'audio_response',
                                'timestamp': datetime.now().isoformat()
                            }
                    else:
                        # Use the traditional approach: transcribe, then process, then TTS
                        transcription_result = await speech_to_text(data.get('audio_data', ''))
                        
                        if 'error' in transcription_result:
                            response = {
                                'role': 'system',
                                'content': f"Error transcribing audio: {transcription_result['error']}",
                                'type': 'text',
                                'timestamp': datetime.now().isoformat()
                            }
                        else:
                            # Create user message with transcribed text
                            user_message = {
                                'role': 'user',
                                'content': transcription_result['text'],
                                'type': 'text',
                                'original_type': 'audio',
                                'timestamp': datetime.now().isoformat()
                            }
                            
                            # Add to message history
                            client_message_history[client_id].append(user_message)
                            
                            # Process with API (using the transcribed text)
                            response = await execute_openai_call(model_id, client_message_history[client_id], transcription_result['text'])
                            
                            # If TTS is enabled, convert the response to speech
                            if data.get('tts_enabled', False):
                                tts_response = await text_to_speech(
                                    response['content'],
                                    voice=data.get('voice', 'alloy'),
                                    speed=float(data.get('speed', 1.0))
                                )
                                if 'error' not in tts_response:
                                    response['audio_data'] = tts_response.get('audio_data', '')
                                    response['audio_format'] = tts_response.get('format', 'mp3')
                                    response['type'] = 'audio_response'
                
                elif message_type == 'generate_image':  # image generation
                    # Generate image based on prompt and parameters
                    image_response = await generate_image(
                        prompt=data.get('prompt', ''),
                        size=data.get('size', '1024x1024'),
                        quality=data.get('quality', 'standard'),
                        style=data.get('style', 'vivid')
                    )
                    
                    if 'error' in image_response:
                        response = {
                            'role': 'assistant',
                            'content': f"Image generation failed: {image_response['error']}",
                            'type': 'text'
                        }
                    else:
                        # Create a message with the generated image
                        response = {
                            'role': 'assistant',
                            'content': image_response.get('url', ''),
                            'revised_prompt': image_response.get('revised_prompt', ''),
                            'type': 'generated_image'
                        }
                        
                        # Create a user message for the prompt
                        user_message = {
                            'role': 'user',
                            'content': f"Generate an image: {data.get('prompt', '')}",
                            'type': 'text',
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        # Add user message to history
                        client_message_history[client_id].append(user_message)
                
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
