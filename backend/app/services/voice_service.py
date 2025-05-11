# app/services/voice_service.py
import base64
import tempfile
import asyncio
from typing import Dict, Any, Optional, List, Callable
import os

from openai import AsyncOpenAI
from ..utils.config_utils import get_api_key
from ..utils.audio_utils import (
    FFMPEG_PATH, FFMPEG_AVAILABLE,
    convert_audio_format,
    decode_base64_audio,
    encode_audio_to_base64
)

class VoiceService:
    """Service for handling voice operations including STT and TTS."""
    
    def __init__(self):
        self.openai_api_key = get_api_key("openai")
        self.realtime_sessions = {}
    
    async def speech_to_text(self, audio_data: str, prompt: str = None) -> Dict[str, Any]:
        """
        Convert speech to text using OpenAI's Whisper API.
        
        Args:
            audio_data: Base64-encoded audio data
            prompt: Optional prompt to guide the transcription
            
        Returns:
            Dictionary containing the transcribed text or error
        """
        if not self.openai_api_key:
            print("ERROR: OpenAI API key not found in configuration.")
            return {"error": "API key not configured"}
        
        try:
            # Decode the base64 audio data
            audio_info = decode_base64_audio(audio_data)
            if not audio_info:
                return {"error": "Failed to decode audio data"}
            
            binary_audio = audio_info['binary_data']
            audio_format = audio_info['format']
            
            # Convert to WAV if needed and if ffmpeg is available
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
                    audio_format = 'wav'
            
            # Save the audio to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_format}") as temp_file:
                temp_file_path = temp_file.name
                temp_file.write(binary_audio)
            
            # Initialize the OpenAI client
            client = AsyncOpenAI(api_key=self.openai_api_key)
            
            # Send the audio file to the API
            with open(temp_file_path, "rb") as audio_file:
                if prompt:
                    transcript = await client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        prompt=prompt
                    )
                else:
                    transcript = await client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
            
            # Clean up the temporary file
            os.unlink(temp_file_path)
            
            return {"text": transcript.text}
            
        except Exception as e:
            print(f"ERROR: Speech-to-text failed: {str(e)}")
            return {"error": str(e)}
            
    async def text_to_speech(self, text: str, voice: str = "alloy", speed: float = 1.0, response_format: str = "mp3") -> Dict[str, Any]:
        """
        Convert text to speech using OpenAI's TTS API.
        
        Args:
            text: The text to convert to speech
            voice: Voice to use - "alloy", "echo", "fable", "onyx", "nova", or "shimmer"
            speed: Speaking speed (0.25 to 4.0)
            response_format: Audio format - "mp3", "opus", "aac", or "flac"
            
        Returns:
            Dictionary containing the audio data or error
        """
        if not self.openai_api_key:
            print("ERROR: OpenAI API key not found in configuration.")
            return {"error": "API key not configured"}
        
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
voice_service = VoiceService()
