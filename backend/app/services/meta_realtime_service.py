# app/services/meta_realtime_service.py
from fastapi import WebSocket
from typing import Dict, Any, List, Callable, AsyncIterator, Optional
import asyncio
import tempfile
import os
import time
import uuid
import logging
import base64
import re
from openai import AsyncOpenAI

import os
from dotenv import load_dotenv
from ..utils.audio_utils import decode_base64_audio, convert_audio_format, FFMPEG_AVAILABLE

# Load environment variables
load_dotenv()

# Get configuration from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
META_API_KEY = os.getenv("META_API_KEY", "")
AUDIO_MAX_CHUNK_SIZE = int(os.getenv("AUDIO_MAX_CHUNK_SIZE", "16000"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("meta_realtime_service")

class MetaRealtimeService:
    """
    Service for handling real-time voice conversations using Meta's SeamlessStreaming API.
    """
    
    def __init__(self, api_key: str = META_API_KEY):
        """
        Initialize the Meta Realtime Service.
        
        Args:
            api_key: Meta API key (if not provided, uses the one from config)
        """
        self.meta_api_key = api_key
        self._initialize()
        
    def _initialize(self):
        """Initialize service state."""
        # Keep track of active sessions
        self.sessions = {}
        
        # Buffers for audio data
        self.audio_buffers = {}
        
        # Buffers for transcriptions to provide continuity
        self.transcription_buffers = {}
        
        # Store conversation history for each session
        self.conversation_histories = {}
        
        logger.info("Meta Realtime Service initialized")
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a session by ID."""
        return self.sessions.get(session_id)
    
    async def create_session(self, client_id: str, callback: Callable, options: Dict[str, Any] = None) -> str:
        """
        Create a new real-time voice conversation session.
        
        Args:
            client_id: The client's unique identifier
            callback: Callback function to send messages to client
            options: Session options
            
        Returns:
            Session ID
        """
        # Generate a unique session ID
        session_id = f"meta-rt-{uuid.uuid4().hex[:8]}"
        
        # Store session data
        self.sessions[session_id] = {
            'client_id': client_id,
            'active': True,
            'callback': callback,
            'options': options or {},
            'created_at': time.time(),
            'last_activity': time.time()
        }
        
        # Initialize buffers
        self.audio_buffers[session_id] = bytearray()
        self.transcription_buffers[session_id] = ""
        
        # Initialize conversation history with a system prompt
        self.conversation_histories[session_id] = [
            {"role": "system", "content": "You are a helpful assistant in a real-time voice conversation using Meta's SeamlessStreaming technology. Keep your responses natural and conversational. This is a continuous conversation where the user can speak multiple times."}
        ]
        
        logger.info(f"Created Meta real-time session {session_id} for client {client_id}")
        return session_id
    
    async def stop_session(self, session_id: str) -> bool:
        """
        Stop an active session.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if session was active and is now stopped, False otherwise
        """
        session = self.get_session(session_id)
        if session and session['active']:
            session['active'] = False
            
            # Cleanup buffers
            if session_id in self.audio_buffers:
                del self.audio_buffers[session_id]
            
            if session_id in self.transcription_buffers:
                del self.transcription_buffers[session_id]
                
            # Clean up conversation history
            if session_id in self.conversation_histories:
                del self.conversation_histories[session_id]
            
            logger.info(f"Stopped Meta real-time session {session_id}")
            return True
        
        return False
    
    async def process_audio_chunk(self, session_id: str, audio_data: str) -> Dict[str, Any]:
        """
        Process an audio chunk in real-time using Meta's SeamlessStreaming.
        
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
        
        # Save audio to temporary file for transcription
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_format}") as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(binary_audio)
        
        try:
            # Use Meta's SeamlessStreaming for speech-to-text
            transcription_text = await self._meta_speech_to_text(temp_file_path, audio_format)
            
            # Only proceed if we have text to process
            if not transcription_text or transcription_text.strip() == "":
                # Clean up temp file
                os.unlink(temp_file_path)
                return {"status": "no_speech_detected"}
            
            # Update transcription buffer with new content
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
            
            logger.error(f"ERROR processing audio chunk with Meta AI: {str(e)}")
            raise
    
    async def _meta_speech_to_text(self, audio_file_path: str, audio_format: str) -> str:
        """
        Use Meta's SeamlessStreaming for speech-to-text conversion.
        
        This is a placeholder implementation that currently uses the Python client library.
        In a production environment, you would use Meta's official API directly.
        
        Args:
            audio_file_path: Path to the audio file
            audio_format: Format of the audio file
            
        Returns:
            Transcribed text
        """
        # For now, we'll use a simple implementation that returns a placeholder
        # In a real implementation, you would call Meta's API
        try:
            import torch
            from seamless_communication.models.inference import Translator
            
            # Initialize the model (this should be done once and cached)
            translator = Translator(
                model_name_or_path="seamless_streaming_unity",
                vocoder_name_or_path="vocoder_v2",
                device=torch.device("cuda" if torch.cuda.is_available() else "cpu"),
            )
            
            # Perform speech-to-text translation
            with open(audio_file_path, "rb") as f:
                audio_bytes = f.read()
            
            text_output = translator.predict(
                input=audio_bytes,
                task_str="s2tt",  # speech-to-text
                tgt_lang="eng",   # target language is English
            )
            
            return text_output.text
            
        except ImportError:
            logger.warning("Meta SeamlessStreaming library not installed. Using fallback.")
            # Fallback to using OpenAI for transcription if Meta libraries aren't available
            return await self._fallback_openai_transcription(audio_file_path)
    
    async def _fallback_openai_transcription(self, audio_file_path: str) -> str:
        """
        Fallback to OpenAI for transcription if Meta libraries aren't available.
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            Transcribed text
        """
        try:
            client = AsyncOpenAI(api_key=OPENAI_API_KEY)
            
            with open(audio_file_path, "rb") as audio_file:
                transcript = await client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            
            return transcript.text
        except Exception as e:
            logger.error(f"Error in fallback transcription: {str(e)}")
            return ""
    
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
            # Generate text response using Meta's Llama 3 model
            response_text = await self._meta_text_generate(session_id, transcription_text)
            
            # If we have a text response, stream it to the client
            if response_text:
                # Stream text chunks to simulate real-time response
                for chunk in self._split_into_chunks(response_text):
                    if not session['active']:
                        break
                    
                    # Send text delta to the client
                    await callback({
                        'role': 'assistant',
                        'content': chunk,
                        'type': 'text_delta',
                        'is_realtime': True
                    })
                    
                    # Add a small delay to simulate streaming
                    await asyncio.sleep(0.05)
            
            # Generate speech from the response text
            if session['active'] and response_text:
                speech_data = await self._meta_text_to_speech(
                    response_text,
                    voice=options.get('voice', 'default'),
                    speed=options.get('speed', 1.0)
                )
                
                if speech_data:
                    # Send audio response
                    await callback({
                        'role': 'assistant',
                        'content': response_text,
                        'audio_data': speech_data.get('audio_data', ''),
                        'audio_format': speech_data.get('format', 'mp3'),
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
            logger.error(f"ERROR generating Meta AI streaming response: {str(e)}")
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
    
    def _split_into_chunks(self, text: str, chunk_size: int = 10) -> List[str]:
        """Split text into small chunks for streaming."""
        words = text.split()
        chunks = []
        current_chunk = []
        
        for word in words:
            current_chunk.append(word)
            if len(current_chunk) >= chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                
        if current_chunk:
            chunks.append(' '.join(current_chunk))
            
        return chunks
    
    async def _meta_text_generate(self, session_id: str, user_input: str) -> str:
        """
        Generate text response using Meta's Llama 3 model.
        
        Args:
            session_id: Session ID
            user_input: User's transcribed input
            
        Returns:
            Generated text response
        """
        # If Meta API integration isn't available, fall back to OpenAI
        try:
            # Add user message to conversation history
            if session_id in self.conversation_histories:
                self.conversation_histories[session_id].append({"role": "user", "content": user_input})
            
            # In a real implementation, you would call Meta's API here
            # For now, we'll use OpenAI as a fallback
            client = AsyncOpenAI(api_key=OPENAI_API_KEY)
            
            # Get the conversation history for this session
            messages = self.conversation_histories[session_id].copy() if session_id in self.conversation_histories else [
                {"role": "system", "content": "You are a helpful assistant in a real-time voice conversation."},
                {"role": "user", "content": user_input}
            ]
            
            # Generate response
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=300,
                temperature=0.7
            )
            
            # Get response text
            assistant_response = response.choices[0].message.content
            
            # Add assistant response to conversation history
            if session_id in self.conversation_histories:
                self.conversation_histories[session_id].append({"role": "assistant", "content": assistant_response})
                
                # Trim conversation history if it gets too long
                if len(self.conversation_histories[session_id]) > 12:  # System message + 10 exchanges
                    # Keep the system message and the last 10 exchanges
                    self.conversation_histories[session_id] = [
                        self.conversation_histories[session_id][0]  # System message
                    ] + self.conversation_histories[session_id][-10:]  # Last 10 messages
            
            return assistant_response
            
        except Exception as e:
            logger.error(f"Error in Meta text generation (using fallback): {str(e)}")
            return f"I apologize, but I'm having trouble processing your request at the moment. Please try again."
    
    async def _meta_text_to_speech(self, text: str, voice: str = "default", speed: float = 1.0) -> Dict[str, Any]:
        """
        Convert text to speech using Meta's TTS API.
        
        Args:
            text: The text to convert to speech
            voice: Voice to use
            speed: Speech speed multiplier
            
        Returns:
            Dictionary with audio data and format
        """
        try:
            # For now, we're falling back to OpenAI for TTS
            client = AsyncOpenAI(api_key=OPENAI_API_KEY)
            
            response = await client.audio.speech.create(
                model="tts-1",
                voice=voice if voice in ["alloy", "echo", "fable", "onyx", "nova", "shimmer"] else "alloy",
                input=text,
                speed=speed
            )
            
            # Get audio data as bytes
            audio_bytes = await response.aread()
            
            # Convert to base64 for transmission
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            return {
                "audio_data": audio_base64,
                "format": "mp3"
            }
            
        except Exception as e:
            logger.error(f"Error in Meta text-to-speech (using fallback): {str(e)}")
            return {}


# Create a singleton instance
meta_realtime_service = MetaRealtimeService()
