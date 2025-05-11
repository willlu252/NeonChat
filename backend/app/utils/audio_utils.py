# app/utils/audio_utils.py
import os
import base64
import tempfile
import subprocess
from typing import Optional, Dict, Any, Union

# Check if ffmpeg is available
def get_ffmpeg_path() -> Optional[str]:
    """
    Find the path to ffmpeg executable.
    
    Returns:
        Path to ffmpeg if found, None otherwise
    """
    # First check if ffmpeg.exe exists in the backend directory
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ffmpeg_path = os.path.join(current_dir, "ffmpeg.exe")
    
    if os.path.exists(ffmpeg_path):
        return ffmpeg_path
    
    # Try to run ffmpeg to check if it's installed globally
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return 'ffmpeg'  # Return just the command name to use global installation
    except (subprocess.SubprocessError, FileNotFoundError):
        return None

FFMPEG_PATH = get_ffmpeg_path()
FFMPEG_AVAILABLE = FFMPEG_PATH is not None

def convert_audio_format(binary_audio: bytes, source_format: str = 'webm', target_format: str = 'wav',
                        sample_rate: int = 16000, channels: int = 1) -> Optional[bytes]:
    """
    Convert audio from one format to another using ffmpeg.
    
    Args:
        binary_audio: The binary audio data
        source_format: Source audio format (e.g., 'webm', 'mp3')
        target_format: Target audio format (e.g., 'wav')
        sample_rate: Target sample rate in Hz
        channels: Number of audio channels (1 for mono, 2 for stereo)
        
    Returns:
        Binary data of the converted audio, or None if conversion fails
    """
    if not FFMPEG_AVAILABLE:
        print("WARNING: ffmpeg not available. Audio format conversion will not work.")
        return None
    
    try:
        # Save the original audio to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{source_format}") as temp_input_file:
            temp_input_path = temp_input_file.name
            temp_input_file.write(binary_audio)
        
        # Create a temporary output file for the converted data
        temp_output_path = temp_input_path + f".{target_format}"
        
        # Use ffmpeg to convert to the target format
        cmd = [
            FFMPEG_PATH,
            '-i', temp_input_path,
            '-acodec', 'pcm_s16le' if target_format == 'wav' else 'libmp3lame',
            '-ar', str(sample_rate),
            '-ac', str(channels),
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
        
        # Read the converted audio
        with open(temp_output_path, 'rb') as f:
            converted_audio = f.read()
        
        # Clean up temporary files
        os.unlink(temp_input_path)
        os.unlink(temp_output_path)
        
        return converted_audio
    except Exception as e:
        print(f"ERROR: Audio conversion failed: {str(e)}")
        return None

def decode_base64_audio(audio_data: str) -> Optional[Dict[str, Any]]:
    """
    Decode base64 encoded audio data and detect format.
    
    Args:
        audio_data: Base64 encoded audio data, optionally with MIME type prefix
        
    Returns:
        Dictionary with binary_data and format, or None if decoding fails
    """
    try:
        audio_format = 'wav'  # Default format
        
        # Check if the audio_data contains format information
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
            
            # Decode the base64 data
            binary_data = base64.b64decode(audio_data.split(',')[1])
        else:
            # Assume it's just base64 without MIME type
            binary_data = base64.b64decode(audio_data)
        
        return {
            'binary_data': binary_data,
            'format': audio_format
        }
    except Exception as e:
        print(f"ERROR: Failed to decode base64 audio: {str(e)}")
        return None

def encode_audio_to_base64(binary_data: bytes, audio_format: str = 'mp3') -> str:
    """
    Encode binary audio data to base64 with appropriate MIME type.
    
    Args:
        binary_data: Binary audio data
        audio_format: Audio format (e.g., 'mp3', 'wav')
        
    Returns:
        Base64 encoded audio data with MIME type prefix
    """
    mime_types = {
        'mp3': 'audio/mpeg',
        'wav': 'audio/wav',
        'webm': 'audio/webm',
        'ogg': 'audio/ogg'
    }
    
    mime_type = mime_types.get(audio_format.lower(), f'audio/{audio_format}')
    base64_data = base64.b64encode(binary_data).decode('utf-8')
    
    return f"data:{mime_type};base64,{base64_data}"
