# app/services/realtime_service.py
import base64
import tempfile
import asyncio
import time
from typing import Dict, Any, Optional, List, Callable, AsyncIterator
import os
import uuid

from openai import AsyncOpenAI
from ..utils.config_utils import get_api_key
from ..utils.audio_utils import (
    FFMPEG_PATH, FFMPEG_AVAILABLE,
    convert_audio_format,
    decode_base64_audio,
    encode_audio_to_base64
)
from ..models.session import Session

class RealtimeService:
    """Service for handling real-time voice conversations."""
    
    def __init__(self):
        self.openai_api_key = get_api_key("openai")
        self.active_sessions = {}
        self.audio_buffers = {}
        self.transcription_buffers = {}
        self.conversation_histories = {}  # Store conversation history for each session
    
    async def create_session(self, client_id: str, callback: Callable, options: Dict[str, Any] = None) -> str:
        """
        Create a new real-time conversation session.
        
        Args:
            client_id: The client's unique identifier
            callback: Async callback function to send events to the client
            options: Session configuration options
            
        Returns:
            Session ID
        """
        if not self.openai_api_key:
            print("ERROR: OpenAI API key not found in configuration.")
            raise ValueError("API key not configured")
        
        # Generate a session ID
        session_id = str(uuid.uuid4())
        
        # Get session options with defaults
        options = options or {}
        voice = options.get('voice', 'alloy')
        speed = float(options.get('speed', 1.0))
        
        # Initialize conversation history for this session
        self.conversation_histories[session_id] = [
            {"role": "system", "content": "You are a helpful assistant in a real-time voice conversation. Keep responses concise and natural."}
        ]
        max_tokens = int(options.get('max_tokens', 150))
        model = options.get('model', 'gpt-4o')
        stream = options.get('stream', True)
        
        # Create session object
        session = Session(
            id=session_id,
            client_id=client_id,
            created_at=time.time(),
            updated_at=time.time(),
            voice_settings={
                'voice': voice,
                'speed': speed
            }
        )
        
        # Store session data
        self.active_sessions[session_id] = {
            'session': session,
            'callback': callback,
            'audio_buffer': bytearray(),
            'transcription_buffer': "",
            'active': True,
            'client_id': client_id,
            'last_activity': time.time(),
            'options': {
                'voice': voice,
                'speed': speed,
                'max_tokens': max_tokens,
                'model': model,
                'stream': stream
            }
        }
        
        # Initialize audio buffer for this session
        self.audio_buffers[session_id] = bytearray()
        self.transcription_buffers[session_id] = ""
        
        print(f"Created realtime session {session_id} for client {client_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data by session ID.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session data or None if not found
        """
        return self.active_sessions.get(session_id)
    
    async def stop_session(self, session_id: str) -> bool:
        """
        Stop an active session.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if session was stopped, False if session not found
        """
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['active'] = False
            
            # Clean up any resources
            # Clean up buffers
            if session_id in self.audio_buffers:
                del self.audio_buffers[session_id]
            
            if session_id in self.transcription_buffers:
                del self.transcription_buffers[session_id]
            
            # Clean up conversation history
            if session_id in self.conversation_histories:
                del self.conversation_histories[session_id]
            
            # Remove session after a short delay to allow ongoing operations to complete
            await asyncio.sleep(0.5)
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            print(f"Stopped realtime session {session_id}")
            return True
        
        return False
    
    async def process_audio_chunk(self, session_id: str, audio_data: str) -> Dict[str, Any]:
        """
        Process an audio chunk in real-time.
        
        Args:
            session_id: Session ID
            audio_data: Base64-encoded audio data
            
        Returns:
            Processing result
        """
        session = self.get_session(session_id)
        if not session or not session['active']:
            raise ValueError(f"Session {session_id} not found or inactive")
        
        # Decode audio data
        audio_info = decode_base64_audio(audio_data)
        if not audio_info:
            raise ValueError("Failed to decode audio data")
        
        binary_audio = audio_info['binary_data']
        audio_format = audio_info['format']
        
        # Append to audio buffer (for future use)
        self.audio_buffers[session_id].extend(binary_audio)
        
        # Convert audio format if needed
        if audio_format != 'wav' and FFMPEG_AVAILABLE:
            converted_audio = convert_audio_format(
                binary_audio, 
                source_format=audio_format,
                target_format='wav',
                sample_rate=16000,
                channels=1
            )
            if converted_audio:
                binary_audio = converted_audio
        
        # Save audio to temporary file for transcription
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(binary_audio)
        
        try:
            # Transcribe audio
            client = AsyncOpenAI(api_key=self.openai_api_key)
            
            with open(temp_file_path, "rb") as audio_file:
                transcript = await client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    prompt=self.transcription_buffers.get(session_id, "")  # Use previous transcript as context
                )
            
            # Update transcription buffer with new content
            transcription_text = transcript.text
            self.transcription_buffers[session_id] = transcription_text
            
            # Trigger the callback to notify of transcription
            callback = session['callback']
            await callback({
                'role': 'system',
                'content': transcription_text,
                'type': 'transcription',
                'is_realtime': True
            })
            
            # Start processing the response in a background task
            # This allows us to return immediately while response generation happens
            asyncio.create_task(self._generate_streaming_response(session_id, transcription_text))
            
            # Clean up temp file
            os.unlink(temp_file_path)
            
            # Update session last activity
            session['last_activity'] = time.time()
            
            return {
                "status": "processing",
                "transcription": transcription_text
            }
            
        except Exception as e:
            # Clean up temp file in case of error
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            
            print(f"ERROR processing audio chunk: {str(e)}")
            raise
    
    async def _generate_streaming_response(self, session_id: str, transcription_text: str):
        """
        Generate a streaming response to the transcribed text.
        
        Args:
            session_id: Session ID
            transcription_text: Transcribed user speech
        """
        session = self.get_session(session_id)
        if not session or not session['active']:
            return
        
        callback = session['callback']
        options = session['options']
        
        try:
            client = AsyncOpenAI(api_key=self.openai_api_key)
            
            # Stream text response
            response_text = ""
            # Make sure session_id is included in options for conversation history tracking
            options_with_session = options.copy()
            options_with_session['session_id'] = session_id
            async for text_chunk in self._stream_text_response(client, transcription_text, options_with_session):
                if not session['active']:
                    break
                
                response_text += text_chunk
                
                # Send text delta to the client
                await callback({
                    'role': 'assistant',
                    'content': text_chunk,
                    'type': 'text_delta',
                    'is_realtime': True
                })
            
            # After text streaming is complete, generate audio for the whole response
            if session['active'] and response_text:
                tts_response = await self._text_to_speech(
                    response_text,
                    voice=options.get('voice', 'alloy'),
                    speed=options.get('speed', 1.0)
                )
                
                if 'error' not in tts_response:
                    # Send audio response
                    await callback({
                        'role': 'assistant',
                        'content': response_text,
                        'audio_data': tts_response.get('audio_data', ''),
                        'audio_format': tts_response.get('format', 'mp3'),
                        'type': 'audio_response',
                        'is_realtime': True
                    })
            
            # Signal completion
            if session['active']:
                await callback({
                    'role': 'system',
                    'content': 'Response complete',
                    'type': 'response_done',
                    'is_realtime': True
                })
                
        except Exception as e:
            print(f"ERROR generating streaming response: {str(e)}")
            # Try to notify the client
            try:
                if session['active']:
                    await callback({
                        'role': 'system',
                        'content': f"Error generating response: {str(e)}",
                        'type': 'error',
                        'is_realtime': True
                    })
            except:
                pass
    
    async def _stream_text_response(self, client: AsyncOpenAI, user_input: str, options: Dict[str, Any]) -> AsyncIterator[str]:
        """
        Stream text response for the given input.
        
        Args:
            client: OpenAI client
            user_input: User's transcribed input
            options: Response generation options
            
        Yields:
            Text chunks as they are generated
        """
        model = options.get('model', 'gpt-4o')
        max_tokens = options.get('max_tokens', 300) # Increased max tokens for more detailed responses
        session_id = options.get('session_id')
        
        print(f"Processing realtime voice input for session {session_id}: '{user_input}'")
        
        # Initialize conversation history if it doesn't exist
        if session_id not in self.conversation_histories:
            print(f"Initializing new conversation history for session {session_id}")
            self.conversation_histories[session_id] = [
                {"role": "system", "content": "You are a helpful assistant in a real-time voice conversation. Keep responses natural and conversational. Remember previous exchanges to maintain context. This is a continuous conversation where the user can speak multiple times."}
            ]
        
        # Add user message to conversation history
        self.conversation_histories[session_id].append({"role": "user", "content": user_input})
        
        # Get the conversation history for this session
        messages = self.conversation_histories[session_id].copy()
        
        print(f"Conversation history for session {session_id} has {len(messages)} messages")
        
        # Create the completion with conversation history
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            stream=True,
            temperature=0.7
        )
        
        # Collect the assistant's response to add to history
        assistant_response = ""
        async for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content:
                assistant_response += delta.content
                yield delta.content
        
        # Add the assistant's response to conversation history
        if assistant_response and session_id in self.conversation_histories:
            self.conversation_histories[session_id].append({"role": "assistant", "content": assistant_response})
            print(f"Added assistant response to history for session {session_id}, history now has {len(self.conversation_histories[session_id])} messages")
            
            # Trim conversation history if it gets too long (keep last 10 messages)
            if len(self.conversation_histories[session_id]) > 12:  # System message + 10 exchanges
                # Keep the system message and the last 10 exchanges
                self.conversation_histories[session_id] = [
                    self.conversation_histories[session_id][0]  # System message
                ] + self.conversation_histories[session_id][-10:]  # Last 10 messages
                print(f"Trimmed conversation history for session {session_id}")
        
        # Update session activity timestamp
        session = self.get_session(session_id)
        if session:
            session['last_activity'] = time.time()
    
    async def _text_to_speech(self, text: str, voice: str = "alloy", speed: float = 1.0, response_format: str = "mp3") -> Dict[str, Any]:
        """
        Convert text to speech using OpenAI's TTS API.
        
        Args:
            text: The text to convert to speech
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            speed: Speaking speed (0.25 to 4.0)
            response_format: Audio format
            
        Returns:
            Dictionary with audio data or error
        """
        try:
            client = AsyncOpenAI(api_key=self.openai_api_key)
            response = await client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
                speed=speed,
                response_format=response_format
            )
            
            # Convert the binary response to base64 for sending over WebSocket
            audio_data = base64.b64encode(await response.read()).decode('utf-8')
            return {
                "audio_data": audio_data,
                "format": response_format
            }
        except Exception as e:
            print(f"ERROR: Text-to-speech failed: {str(e)}")
            return {"error": str(e)}

# Create a global service instance
realtime_service = RealtimeService()
