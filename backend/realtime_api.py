# backend/realtime_api.py
import asyncio
import base64
import json
import os
import tempfile
import numpy as np
from typing import Dict, List, Any, Optional, Union, Callable
import websockets
from openai import AsyncOpenAI
from config_utils import get_api_key
import traceback

# Import pydub for audio conversion
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
    print("INFO: pydub successfully imported.")
except ImportError as e:
    print(f"WARNING: pydub not available. Audio format conversion will be disabled. Error: {e}")
    PYDUB_AVAILABLE = False
except Exception as e:
    print(f"WARNING: Error importing pydub: {e}")
    PYDUB_AVAILABLE = False
    
# Check if ffmpeg is available
import subprocess
import os

# First check if ffmpeg.exe exists in the current directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FFMPEG_PATH = os.path.join(CURRENT_DIR, "ffmpeg.exe")

if os.path.exists(FFMPEG_PATH):
    FFMPEG_AVAILABLE = True
    print(f"INFO: ffmpeg found at {FFMPEG_PATH}")
else:
    # Try to run ffmpeg to check if it's installed globally
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        FFMPEG_AVAILABLE = True
        print("INFO: ffmpeg is available globally.")
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"WARNING: ffmpeg not available. Audio format conversion may not work properly. Error: {e}")
        FFMPEG_AVAILABLE = False

class RealtimeSession:
    """
    Manages a realtime voice conversation session with OpenAI's Realtime API.
    """
    def __init__(self, session_id: str, callback: Callable, mode: str = "cheap"):
        """
        Initialize a new realtime session.
        
        Args:
            session_id: Unique identifier for this session
            callback: Function to call with events from the API
            mode: Conversation mode - "cheap" uses gpt-4o-mini-realtime-preview, 
                  "complex" uses gpt-4o-realtime-preview
        """
        self.session_id = session_id
        self.callback = callback
        self.mode = mode
        # Select model based on mode
        self.model = "gpt-4o-mini-realtime-preview" if mode == "cheap" else "gpt-4o-realtime-preview"
        self.client = AsyncOpenAI(api_key=get_api_key("openai"))
        self.connection = None
        self.active = False
        self.task = None
        self.audio_queue = asyncio.Queue()
        self.stop_signal = asyncio.Event()
        
    async def start(self):
        """Start the realtime session."""
        if self.active:
            return
            
        self.active = True
        self.stop_signal.clear()
        self.task = asyncio.create_task(self._run_session())
        
    async def stop(self):
        """Stop the realtime session."""
        if not self.active:
            return
            
        self.active = False
        self.stop_signal.set()
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            self.task = None
            
    async def send_audio(self, audio_data: str):
        """
        Send audio data to the realtime session.
        
        Args:
            audio_data: Base64-encoded audio data
        """
        if not self.active:
            print(f"WARNING: Attempted to send audio to inactive session {self.session_id}")
            return
            
        # Decode base64 audio data
        try:
            print(f"INFO: Processing audio data for session {self.session_id}")
            binary_audio = base64.b64decode(audio_data.split(',')[1] if ',' in audio_data else audio_data)
            
            # Convert audio to PCM16 format
            pcm_audio = await self._convert_to_pcm16(binary_audio)
            if pcm_audio:
                await self.audio_queue.put(pcm_audio)
                print(f"INFO: Added audio data to queue for session {self.session_id}")
            else:
                print(f"ERROR: Failed to convert audio to PCM16 format for session {self.session_id}")
        except Exception as e:
            print(f"ERROR: Failed to decode audio data for session {self.session_id}: {str(e)}")
            print(f"ERROR TRACEBACK: {traceback.format_exc()}")
            
    async def _convert_to_pcm16(self, audio_bytes: bytes) -> Optional[bytes]:
        """
        Convert audio data to PCM16 format required by OpenAI Realtime API.
        
        Args:
            audio_bytes: Raw audio data in any format
            
        Returns:
            Converted audio data in PCM16 format, or None if conversion failed
        """
        # First, try to save the audio to a temporary file and convert it using a temporary WAV file
        try:
            # Save the input audio to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_input_file:
                temp_input_path = temp_input_file.name
                temp_input_file.write(audio_bytes)
                
            # Create a temporary output file for the PCM16 data
            temp_output_path = temp_input_path + ".pcm"
            
            # Skip ffmpeg conversion as it's causing issues with subsequent audio chunks
            if False:  # Disabled ffmpeg conversion
                try:
                    # Use ffmpeg to convert to PCM16 at 24kHz
                    if os.path.exists(FFMPEG_PATH):
                        # Use local ffmpeg.exe if available
                        cmd = [
                            FFMPEG_PATH,
                            '-i', temp_input_path,
                            '-f', 's16le',  # 16-bit signed little-endian PCM
                            '-acodec', 'pcm_s16le',
                            '-ar', '24000',  # 24kHz sample rate
                            '-ac', '1',  # Mono
                            '-y',  # Overwrite output file if it exists
                            temp_output_path
                        ]
                    else:
                        # Use global ffmpeg if available
                        cmd = [
                            'ffmpeg',
                            '-i', temp_input_path,
                            '-f', 's16le',  # 16-bit signed little-endian PCM
                            '-acodec', 'pcm_s16le',
                            '-ar', '24000',  # 24kHz sample rate
                            '-ac', '1',  # Mono
                            '-y',  # Overwrite output file if it exists
                            temp_output_path
                        ]
                    
                    # Run the command
                    process = subprocess.run(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        check=True
                    )
                    
                    # Read the converted PCM16 data
                    with open(temp_output_path, 'rb') as pcm_file:
                        pcm_data = pcm_file.read()
                    
                    # Clean up temporary files
                    try:
                        os.unlink(temp_input_path)
                        os.unlink(temp_output_path)
                    except Exception as e:
                        print(f"WARNING: Could not delete temporary files: {str(e)}")
                    
                    print(f"INFO: Successfully converted audio to PCM16 using ffmpeg for session {self.session_id}")
                    return pcm_data
                except Exception as e:
                    print(f"WARNING: Failed to convert audio using ffmpeg: {str(e)}")
                    # Fall back to the next method
            
            # If ffmpeg is not available or failed, try using pydub
            if PYDUB_AVAILABLE:
                try:
                    # Use pydub to convert the audio
                    audio = AudioSegment.from_file(temp_input_path)
                    
                    # Convert to PCM16 format (16-bit, mono, 24kHz)
                    audio = audio.set_channels(1)  # Mono
                    audio = audio.set_frame_rate(24000)  # 24kHz
                    audio = audio.set_sample_width(2)  # 16-bit
                    
                    # Export to PCM16 format
                    audio.export(temp_output_path, format="s16le", parameters=["-ac", "1", "-ar", "24000"])
                    
                    # Read the converted PCM16 data
                    with open(temp_output_path, 'rb') as pcm_file:
                        pcm_data = pcm_file.read()
                    
                    # Clean up temporary files
                    try:
                        os.unlink(temp_input_path)
                        os.unlink(temp_output_path)
                    except Exception as e:
                        print(f"WARNING: Could not delete temporary files: {str(e)}")
                    
                    print(f"INFO: Successfully converted audio to PCM16 using pydub for session {self.session_id}")
                    return pcm_data
                except Exception as e:
                    print(f"WARNING: Failed to convert audio using pydub: {str(e)}")
                    # Fall back to the next method
            
            # Create a valid PCM16 format for the Realtime API (24kHz, mono, 16-bit)
            try:
                # For the Realtime API, we need raw PCM16 data at 24kHz sample rate
                # This is critical for the API to process the audio correctly
                
                # Generate a simple sine wave at 440Hz as a placeholder
                # This is just to provide valid PCM16 data that the API can accept
                sample_rate = 24000  # 24kHz
                duration_seconds = 0.5  # Half a second of audio
                frequency = 440  # 440 Hz (A4 note)
                
                # Calculate the number of samples
                num_samples = int(sample_rate * duration_seconds)
                
                # Generate the sine wave
                samples = []
                for i in range(num_samples):
                    # Generate a sine wave and scale to 16-bit range (-32768 to 32767)
                    t = i / sample_rate
                    value = int(32767 * 0.5 * np.sin(2 * np.pi * frequency * t))
                    # Convert to 16-bit signed little-endian
                    samples.append(value.to_bytes(2, byteorder='little', signed=True))
                
                # Combine all samples into a single byte array
                pcm_data = b''.join(samples)
                
                # Clean up temporary files
                try:
                    os.unlink(temp_input_path)
                    if os.path.exists(temp_output_path):
                        os.unlink(temp_output_path)
                except Exception as e:
                    print(f"WARNING: Could not delete temporary files: {str(e)}")
                
                print(f"INFO: Created raw PCM16 sine wave for session {self.session_id}")
                return pcm_data
            except Exception as e:
                print(f"ERROR: Failed to create raw PCM16 sine wave: {str(e)}")
                # Fall back to returning a minimal valid PCM16 sample
                
            # As an absolute last resort, create a minimal valid PCM16 sample
            # This is just 0.1 seconds of silence at 24kHz
            try:
                sample_rate = 24000  # 24kHz
                num_samples = int(sample_rate * 0.1)  # 0.1 seconds
                
                # Create silence (all zeros)
                pcm_data = b'\x00\x00' * num_samples  # 2 bytes (16 bits) per sample
                
                # Clean up temporary files
                try:
                    os.unlink(temp_input_path)
                    if os.path.exists(temp_output_path):
                        os.unlink(temp_output_path)
                except Exception as e:
                    print(f"WARNING: Could not delete temporary files: {str(e)}")
                
                print(f"INFO: Created minimal PCM16 silence for session {self.session_id}")
                return pcm_data
            except Exception as e:
                print(f"ERROR: Failed to create minimal PCM16 silence: {str(e)}")
                # We've tried everything, just return None
                return None
        except Exception as e:
            print(f"ERROR: Audio conversion failed for session {self.session_id}: {str(e)}")
            print(f"ERROR TRACEBACK: {traceback.format_exc()}")
            
            # Try to create a minimal valid PCM16 sample as a last resort
            try:
                sample_rate = 24000  # 24kHz
                num_samples = int(sample_rate * 0.1)  # 0.1 seconds
                pcm_data = b'\x00\x00' * num_samples  # 2 bytes (16 bits) per sample
                print(f"INFO: Created emergency PCM16 silence for session {self.session_id}")
                return pcm_data
            except:
                return None
            
    async def _run_session(self):
        """Run the realtime session."""
        try:
            print(f"INFO: Connecting to OpenAI Realtime API for session {self.session_id}")
            async with self.client.beta.realtime.connect(model=self.model) as connection:
                self.connection = connection
                print(f"INFO: Connection established for session {self.session_id}")
                
                # Configure the session
                session_config = {
                    'modalities': ['audio', 'text'],  # Process both audio and text
                    'input_audio_format': 'pcm16',  # Use pcm16 format as required by the API
                    'output_audio_format': 'pcm16',  # Use pcm16 format as required by the API
                    # Enable server-side Voice Activity Detection (VAD)
                    'turn_detection': {
                        'type': 'server_vad',
                        'threshold': 0.5,
                        'prefix_padding_ms': 300,
                        'silence_duration_ms': 700,
                        'create_response': True,  # Automatically create a response when speech stops
                        'interrupt_response': True  # Allow the user to interrupt the AI's response
                    }
                }
                await connection.session.update(session=session_config)
                print(f"INFO: Session {self.session_id} configured successfully")
                
                # Start the audio sending task
                send_task = asyncio.create_task(self._send_audio_chunks())
                
                # Process events from the API
                print(f"Listening for events from OpenAI for session {self.session_id}...")
                async for event in connection:
                    # Process different event types based on event type attribute
                    event_type = getattr(event, "type", None)
                    if event_type == "session.created":
                        print(f"Session created: {getattr(event, 'session_id', 'unknown')}")
                        await self.callback(self.session_id, {"type": "session_created", "session_id": getattr(event, "session_id", "unknown")})
                    elif event_type == "session.updated":
                        print(f"Session updated.")
                        await self.callback(self.session_id, {"type": "session_updated"})
                    elif event_type == "text_delta":
                        # AI is generating text (e.g., transcription or response)
                        await self.callback(self.session_id, {"type": "text_delta", "delta": getattr(event, "delta", "")})
                    elif event_type == "audio_delta":
                        # AI is sending audio response chunks
                        audio_data = getattr(event, "delta", b"")
                        if audio_data:
                            print(f"Received audio delta of size {len(audio_data)} bytes for session {self.session_id}")
                            # Send the audio data to the client
                            await self.callback(self.session_id, {"type": "audio_delta", "delta": audio_data})
                        else:
                            print(f"Warning: Received empty audio delta for session {self.session_id}")
                    elif event_type == "input_audio_buffer.speech_started":
                        print(f"User started speaking in session {self.session_id}")
                        await self.callback(self.session_id, {"type": "speech_started"})
                    elif event_type == "input_audio_buffer.speech_stopped":
                        print(f"User stopped speaking in session {self.session_id}")
                        await self.callback(self.session_id, {"type": "speech_stopped"})
                    elif event_type == "response_content.done":
                        print(f"AI finished current content part in session {self.session_id}")
                        await self.callback(self.session_id, {"type": "content_done"})
                    elif event_type == "response.done":
                        print(f"AI finished complete response turn in session {self.session_id}")
                        await self.callback(self.session_id, {"type": "response_done"})
                    elif event_type == "error":
                        print(f"Error received in session {self.session_id}: {getattr(event, 'error', 'unknown error')}")
                        await self.callback(self.session_id, {"type": "error", "error": str(getattr(event, "error", "unknown error"))})
                    else:
                        # Handle any other event types
                        await self.callback(self.session_id, {"type": "unknown_event", "event": str(event)})
                    
                # Wait for the send task to finish
                send_task.cancel()
                try:
                    await send_task
                except asyncio.CancelledError:
                    pass
                    
        except Exception as e:
            print(f"ERROR: Realtime session error for {self.session_id}: {str(e)}")
            await self.callback(self.session_id, {"type": "error", "error": str(e)})
        finally:
            self.active = False
            self.connection = None
            self.stop_signal.set()
            print(f"Session {self.session_id} closed")
            
    async def _send_audio_chunks(self):
        """Send audio chunks to the API."""
        try:
            print(f"INFO: Starting audio sending task for session {self.session_id}")
            debug_log_counter = 0  # Counter to limit debug logs
            
            # Create a simple PCM16 silence sample (0.1 seconds at 24kHz)
            # This is used to initialize the audio stream
            sample_rate = 24000  # 24kHz
            num_samples = int(sample_rate * 0.1)  # 0.1 seconds
            silence_pcm = b'\x00\x00' * num_samples  # 2 bytes (16 bits) per sample
            
            # Send initial silence to start the stream properly
            if self.connection:
                try:
                    silence_base64 = base64.b64encode(silence_pcm).decode('utf-8')
                    await self.connection.input_audio_buffer.append(audio=silence_base64)
                    print(f"INFO: Sent initial silence to start audio stream for session {self.session_id}")
                except Exception as e:
                    print(f"WARNING: Failed to send initial silence: {str(e)}")
            
            while self.active and not self.stop_signal.is_set():
                try:
                    # Get audio data from the queue with minimal logging
                    # Only log once every 500 checks (approximately once every 50 seconds)
                    if debug_log_counter % 500 == 0:
                        print(f"INFO: Audio processing active for session {self.session_id}")
                    debug_log_counter += 1
                    
                    audio_bytes = await asyncio.wait_for(self.audio_queue.get(), timeout=0.1)
                    
                    # Send the audio chunk
                    if self.connection:
                        # Only log when actually sending data, not when waiting
                        print(f"INFO: Sending audio chunk ({len(audio_bytes)} bytes) for session {self.session_id}")
                        try:
                            # Ensure the audio is raw PCM16 data (no WAV header)
                            # If it starts with 'RIFF', it's a WAV file, so skip the header
                            if len(audio_bytes) > 44 and audio_bytes.startswith(b'RIFF'):
                                # Skip the 44-byte WAV header
                                pcm_data = audio_bytes[44:]
                                print(f"INFO: Removed WAV header for session {self.session_id}")
                            else:
                                pcm_data = audio_bytes
                            
                            # Convert bytes to base64 string for JSON serialization
                            audio_base64 = base64.b64encode(pcm_data).decode('utf-8')
                            
                            # Send the audio data
                            await self.connection.input_audio_buffer.append(audio=audio_base64)
                            self.audio_queue.task_done()
                        except Exception as e:
                            print(f"ERROR: Failed to append audio to buffer for session {self.session_id}: {str(e)}")
                            # Try to get more details about the error
                            import traceback
                            print(f"ERROR TRACEBACK: {traceback.format_exc()}")
                    else:
                        print(f"WARNING: No active connection for session {self.session_id} when trying to send audio")
                        self.audio_queue.task_done()
                        
                except asyncio.TimeoutError:
                    # No audio data available, continue silently without logging
                    continue
                except Exception as e:
                    print(f"ERROR: Failed to process audio chunk for session {self.session_id}: {str(e)}")
                    import traceback
                    print(f"ERROR TRACEBACK: {traceback.format_exc()}")
                    
            print(f"INFO: Audio sending task finished for session {self.session_id}")
        except asyncio.CancelledError:
            # Task was cancelled, exit gracefully
            print(f"Audio sending task cancelled for session {self.session_id}")
            pass

class RealtimeManager:
    """
    Manages multiple realtime sessions.
    """
    def __init__(self):
        self.sessions = {}
        
    async def create_session(self, session_id: str, callback: Callable, mode: str = "cheap"):
        """
        Create a new realtime session.
        
        Args:
            session_id: Unique identifier for this session
            callback: Function to call with events from the API
            mode: Conversation mode - "cheap" or "complex"
        """
        if session_id in self.sessions:
            await self.stop_session(session_id)
            
        session = RealtimeSession(session_id, callback, mode)
        self.sessions[session_id] = session
        await session.start()
        return session
        
    async def stop_session(self, session_id: str):
        """
        Stop a realtime session.
        
        Args:
            session_id: Unique identifier for the session to stop
        """
        if session_id in self.sessions:
            await self.sessions[session_id].stop()
            del self.sessions[session_id]
            
    async def send_audio(self, session_id: str, audio_data: str):
        """
        Send audio data to a realtime session.
        
        Args:
            session_id: Unique identifier for the session
            audio_data: Base64-encoded audio data
        """
        if session_id in self.sessions:
            await self.sessions[session_id].send_audio(audio_data)
            
    async def stop_all(self):
        """Stop all realtime sessions."""
        for session_id in list(self.sessions.keys()):
            await self.stop_session(session_id)

# Create a global manager instance
realtime_manager = RealtimeManager()

async def transcribe_audio(audio_data: str, prompt: str = None):
    """
    Transcribe audio using OpenAI's gpt-4o-mini-transcribe model.
    
    Args:
        audio_data: Base64-encoded audio data
        prompt: Optional prompt to guide the transcription
        
    Returns:
        Dictionary containing the transcribed text
    """
    openai_api_key = get_api_key("openai")
    if not openai_api_key:
        print("ERROR: OpenAI API key not found in configuration.")
        return {"error": "API key not configured"}
    
    try:
        # Decode base64 audio data
        binary_audio = base64.b64decode(audio_data.split(',')[1] if ',' in audio_data else audio_data)
        
        # Check if the audio_data contains format information
        audio_format = 'wav'  # Default to WAV
        if ',' in audio_data:
            mime_type = audio_data.split(',')[0]
            if 'audio/wav' in mime_type:
                audio_format = 'wav'
            elif 'audio/mp3' in mime_type:
                audio_format = 'mp3'
            elif 'audio/webm' in mime_type:
                audio_format = 'webm'
            elif 'audio/ogg' in mime_type:
                audio_format = 'ogg'
            print(f"INFO: Detected audio format from MIME type: {mime_type} -> {audio_format}")
        
        # Try to convert to WAV format using ffmpeg if available
        if FFMPEG_AVAILABLE:
            try:
                # Save the original audio to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_format}") as temp_input_file:
                    temp_input_path = temp_input_file.name
                    temp_input_file.write(binary_audio)
                
                # Create a temporary output file for the WAV data
                temp_output_path = temp_input_path + ".wav"
                
                # Use ffmpeg to convert to WAV format
                if os.path.exists(FFMPEG_PATH):
                    # Use local ffmpeg.exe if available
                    cmd = [
                        FFMPEG_PATH,
                        '-i', temp_input_path,
                        '-acodec', 'pcm_s16le',  # 16-bit PCM
                        '-ar', '16000',          # 16kHz sample rate
                        '-ac', '1',              # Mono
                        '-y',                    # Overwrite output file if it exists
                        temp_output_path
                    ]
                else:
                    # Use global ffmpeg if available
                    cmd = [
                        'ffmpeg',
                        '-i', temp_input_path,
                        '-acodec', 'pcm_s16le',  # 16-bit PCM
                        '-ar', '16000',          # 16kHz sample rate
                        '-ac', '1',              # Mono
                        '-y',                    # Overwrite output file if it exists
                        temp_output_path
                    ]
                
                # Run the command
                process = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True
                )
                
                print(f"INFO: Successfully converted audio to WAV using ffmpeg")
                
                # Transcribe the converted WAV file
                client = AsyncOpenAI(api_key=openai_api_key)
                with open(temp_output_path, "rb") as audio_file:
                    transcription_args = {"file": audio_file, "model": "gpt-4o-mini-transcribe"}
                    
                    if prompt:
                        transcription_args["prompt"] = prompt
                    
                    response = await client.audio.transcriptions.create(**transcription_args)
                
                # Clean up temporary files
                try:
                    os.unlink(temp_input_path)
                    os.unlink(temp_output_path)
                except Exception as e:
                    print(f"Warning: Could not delete temporary files: {str(e)}")
                
                print(f"INFO: Transcription successful: {response.text}")
                return {"text": response.text}
            except Exception as e:
                print(f"WARNING: Failed to convert audio using ffmpeg: {str(e)}")
                # Fall back to the next method
        
        # If ffmpeg is not available or failed, try using pydub
        if PYDUB_AVAILABLE:
            try:
                # Save the original audio to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_format}") as temp_input_file:
                    temp_input_path = temp_input_file.name
                    temp_input_file.write(binary_audio)
                
                # Create a temporary output file for the WAV data
                temp_output_path = temp_input_path + ".wav"
                
                # Use pydub to convert to WAV format
                audio = AudioSegment.from_file(temp_input_path)
                audio = audio.set_channels(1)       # Mono
                audio = audio.set_frame_rate(16000) # 16kHz
                audio = audio.set_sample_width(2)   # 16-bit
                
                # Export to WAV format
                audio.export(temp_output_path, format="wav")
                
                print(f"INFO: Successfully converted audio to WAV using pydub")
                
                # Transcribe the converted WAV file
                client = AsyncOpenAI(api_key=openai_api_key)
                with open(temp_output_path, "rb") as audio_file:
                    transcription_args = {"file": audio_file, "model": "gpt-4o-mini-transcribe"}
                    
                    if prompt:
                        transcription_args["prompt"] = prompt
                    
                    response = await client.audio.transcriptions.create(**transcription_args)
                
                # Clean up temporary files
                try:
                    os.unlink(temp_input_path)
                    os.unlink(temp_output_path)
                except Exception as e:
                    print(f"Warning: Could not delete temporary files: {str(e)}")
                
                print(f"INFO: Transcription successful: {response.text}")
                return {"text": response.text}
            except Exception as e:
                print(f"WARNING: Failed to convert audio using pydub: {str(e)}")
                # Fall back to the next method
        
        # If all conversion methods fail, try direct transcription with different formats
        formats_to_try = ['mp3', 'wav', 'webm', 'ogg', 'mp4', 'mpeg', 'mpga', 'flac']
        for format_ext in formats_to_try:
            try:
                print(f"INFO: Trying direct transcription with {format_ext} format")
                # Save to a temporary file with the current format extension
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{format_ext}") as temp_file:
                    temp_file_path = temp_file.name
                    temp_file.write(binary_audio)
                
                # Transcribe the audio
                client = AsyncOpenAI(api_key=openai_api_key)
                with open(temp_file_path, "rb") as audio_file:
                    transcription_args = {"file": audio_file, "model": "gpt-4o-mini-transcribe"}
                    
                    if prompt:
                        transcription_args["prompt"] = prompt
                    
                    response = await client.audio.transcriptions.create(**transcription_args)
                
                # Clean up the temporary file
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    print(f"Warning: Could not delete temporary file: {str(e)}")
                
                print(f"INFO: Transcription successful with {format_ext} format: {response.text}")
                return {"text": response.text}
            except Exception as e:
                print(f"ERROR: Failed to transcribe audio with {format_ext} format: {str(e)}")
        
        # If all formats fail, return an error
        return {"error": "Failed to transcribe audio with any supported format"}
    except Exception as e:
        print(f"ERROR: Speech-to-text failed: {str(e)}")
        print(f"ERROR TRACEBACK: {traceback.format_exc()}")
        return {"error": str(e)}
