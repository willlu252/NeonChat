# backend/api_calls.py
import os
import openai
import base64
import tempfile
from typing import Dict, List, Any, Optional, Union
from config_utils import get_api_key
from file_utils import process_file_content
from realtime_api import FFMPEG_PATH

async def generate_image(prompt: str, size: str = "1024x1024", quality: str = "standard", style: str = "vivid"):
    """
    Generate an image using OpenAI's DALL-E 3 API
    
    Args:
        prompt: The text prompt to generate an image from
        size: Image size - "1024x1024", "1792x1024", or "1024x1792"
        quality: Image quality - "standard" or "hd"
        style: Image style - "vivid" or "natural"
        
    Returns:
        Dictionary containing the generated image data
    """
    openai_api_key = get_api_key("openai")
    if not openai_api_key:
        print("ERROR: OpenAI API key not found in configuration.")
        return {"error": "API key not configured"}
    
    try:
        client = openai.AsyncOpenAI(api_key=openai_api_key)
        response = await client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality=quality,
            style=style,
            n=1
        )
        
        # Return the image URL or base64 data
        return {
            "url": response.data[0].url,
            "revised_prompt": response.data[0].revised_prompt
        }
    except Exception as e:
        print(f"ERROR: Image generation failed: {str(e)}")
        return {"error": str(e)}

async def text_to_speech(text: str, voice: str = "alloy", speed: float = 1.0, response_format: str = "mp3"):
    """
    Convert text to speech using OpenAI's TTS API
    
    Args:
        text: The text to convert to speech
        voice: Voice to use - "alloy", "echo", "fable", "onyx", "nova", or "shimmer"
        speed: Speaking speed (0.25 to 4.0)
        response_format: Audio format - "mp3", "opus", "aac", or "flac"
        
    Returns:
        Dictionary containing the audio data
    """
    openai_api_key = get_api_key("openai")
    if not openai_api_key:
        print("ERROR: OpenAI API key not found in configuration.")
        return {"error": "API key not configured"}
    
    try:
        client = openai.AsyncOpenAI(api_key=openai_api_key)
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

async def speech_to_text(audio_data: str, prompt: str = None):
    """
    Convert speech to text using OpenAI's Whisper API
    
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
        
        # Skip ffmpeg conversion for subsequent audio chunks as it's causing issues
        # Try direct transcription with different formats instead
        if False:  # Disabled ffmpeg conversion
            try:
                # Save the original audio to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_format}") as temp_input_file:
                    temp_input_path = temp_input_file.name
                    temp_input_file.write(binary_audio)
                
                # Create a temporary output file for the WAV data
                temp_output_path = temp_input_path + ".wav"
                
                # Use ffmpeg to convert to WAV format
                cmd = [
                    FFMPEG_PATH,
                    '-i', temp_input_path,
                    '-acodec', 'pcm_s16le',  # 16-bit PCM
                    '-ar', '16000',          # 16kHz sample rate
                    '-ac', '1',              # Mono
                    '-y',                    # Overwrite output file if it exists
                    temp_output_path
                ]
                
                # Run the command
                import subprocess
                process = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True
                )
                
                print(f"INFO: Successfully converted audio to WAV using ffmpeg")
                
                # Transcribe the converted WAV file
                client = openai.AsyncOpenAI(api_key=openai_api_key)
                with open(temp_output_path, "rb") as audio_file:
                    transcription_args = {"file": audio_file, "model": "whisper-1"}
                    
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
        
        # If ffmpeg is not available or failed, try multiple formats
        formats_to_try = [audio_format, 'mp3', 'wav', 'webm', 'ogg', 'mp4', 'mpeg', 'mpga', 'flac']
        
        # Remove duplicates while preserving order
        seen = set()
        formats_to_try = [x for x in formats_to_try if not (x in seen or seen.add(x))]
        
        client = openai.AsyncOpenAI(api_key=openai_api_key)
        last_error = None
        
        # Try each format until one works
        for format_ext in formats_to_try:
            try:
                print(f"INFO: Trying transcription with {format_ext} format")
                # Save to a temporary file with the current format extension
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{format_ext}") as temp_file:
                    temp_file_path = temp_file.name
                    temp_file.write(binary_audio)
                
                # Transcribe the audio
                with open(temp_file_path, "rb") as audio_file:
                    transcription_args = {"file": audio_file, "model": "whisper-1"}
                    
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
                last_error = e
                # Continue to the next format
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
        
        # If all formats fail, return the last error
        return {"error": f"Failed to transcribe audio with any supported format: {str(last_error)}"}
    except Exception as e:
        print(f"ERROR: Speech-to-text failed: {str(e)}")
        return {"error": str(e)}

async def conversational_voice_chat(audio_data: str, message_history: List[Dict[str, Any]], voice: str = "alloy", audio_format: str = "mp3"):
    """
    Create a conversational voice chat using OpenAI's gpt-4o-audio-preview model
    
    Args:
        audio_data: Base64-encoded audio data
        message_history: Previous conversation history
        voice: Voice to use (alloy, echo, fable, onyx, nova, or shimmer)
        audio_format: Audio format for the response (mp3, wav, etc.)
        
    Returns:
        Dictionary containing the response text and audio data
    """
    openai_api_key = get_api_key("openai")
    if not openai_api_key:
        print("ERROR: OpenAI API key not found in configuration.")
        return {"error": "API key not configured"}
    
    try:
        # Decode base64 audio data
        binary_audio = base64.b64decode(audio_data.split(',')[1] if ',' in audio_data else audio_data)
        
        # Check if the audio_data contains format information
        audio_format_input = 'wav'  # Default to WAV
        if ',' in audio_data:
            mime_type = audio_data.split(',')[0]
            if 'audio/wav' in mime_type:
                audio_format_input = 'wav'
            elif 'audio/mp3' in mime_type:
                audio_format_input = 'mp3'
            elif 'audio/webm' in mime_type:
                audio_format_input = 'webm'
            elif 'audio/ogg' in mime_type:
                audio_format_input = 'ogg'
            print(f"INFO: Detected audio format from MIME type: {mime_type} -> {audio_format_input}")
        
        # Skip ffmpeg conversion for voice chat as it's causing issues
        if False:  # Disabled ffmpeg conversion
            try:
                # Save the original audio to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_format_input}") as temp_input_file:
                    temp_input_path = temp_input_file.name
                    temp_input_file.write(binary_audio)
                
                # Create a temporary output file for the WAV data
                temp_output_path = temp_input_path + ".wav"
                
                # Use ffmpeg to convert to WAV format
                cmd = [
                    FFMPEG_PATH,
                    '-i', temp_input_path,
                    '-acodec', 'pcm_s16le',  # 16-bit PCM
                    '-ar', '16000',          # 16kHz sample rate
                    '-ac', '1',              # Mono
                    '-y',                    # Overwrite output file if it exists
                    temp_output_path
                ]
                
                # Run the command
                import subprocess
                process = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True
                )
                
                print(f"INFO: Successfully converted audio to WAV using ffmpeg")
                
                # Format previous messages for the API
                formatted_messages = []
                for msg in message_history:
                    if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                        continue
                        
                    # Only include user and assistant messages
                    if msg["role"] not in ["user", "assistant"]:
                        continue
                        
                    formatted_messages.append({"role": msg["role"], "content": msg["content"]})
                
                # Create the client and process with the converted WAV file
                client = openai.AsyncOpenAI(api_key=openai_api_key)
                with open(temp_output_path, "rb") as audio_file:
                    # Create the completion with audio input and output
                    response = await client.chat.completions.create(
                        model="gpt-4o-audio-preview",
                        modalities=["text", "audio"],
                        audio={"voice": voice, "format": audio_format},
                        input_audio=audio_file,
                        messages=formatted_messages
                    )
                
                # Clean up temporary files
                try:
                    os.unlink(temp_input_path)
                    os.unlink(temp_output_path)
                except Exception as e:
                    print(f"Warning: Could not delete temporary files: {str(e)}")
                
                # Extract text and audio from the response
                text_content = response.choices[0].message.content
                audio_data_response = None
                
                # Get the audio data if available
                if hasattr(response.choices[0].message, 'audio') and response.choices[0].message.audio:
                    audio_data_response = base64.b64encode(response.choices[0].message.audio).decode('utf-8')
                
                print(f"INFO: Conversational voice chat successful with ffmpeg conversion")
                return {
                    "text": text_content,
                    "audio_data": audio_data_response,
                    "format": audio_format
                }
            except Exception as e:
                print(f"WARNING: Failed to convert audio using ffmpeg: {str(e)}")
                # Fall back to the next method
        
        # If ffmpeg is not available or failed, try multiple formats
        formats_to_try = [audio_format_input, 'mp3', 'wav', 'webm', 'ogg', 'mp4', 'mpeg', 'mpga', 'flac']
        
        # Remove duplicates while preserving order
        seen = set()
        formats_to_try = [x for x in formats_to_try if not (x in seen or seen.add(x))]
        
        # Format previous messages for the API
        formatted_messages = []
        for msg in message_history:
            if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                continue
                
            # Only include user and assistant messages
            if msg["role"] not in ["user", "assistant"]:
                continue
                
            formatted_messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Create the client
        client = openai.AsyncOpenAI(api_key=openai_api_key)
        last_error = None
        
        # Try each format until one works
        for format_ext in formats_to_try:
            try:
                print(f"INFO: Trying conversational voice chat with {format_ext} format")
                # Save to a temporary file with the current format extension
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{format_ext}") as temp_file:
                    temp_file_path = temp_file.name
                    temp_file.write(binary_audio)
                
                # Open the audio file
                with open(temp_file_path, "rb") as audio_file:
                    # Create the completion with audio input and output
                    response = await client.chat.completions.create(
                        model="gpt-4o-audio-preview",
                        modalities=["text", "audio"],
                        audio={"voice": voice, "format": audio_format},
                        input_audio=audio_file,
                        messages=formatted_messages
                    )
                
                # Clean up the temporary file
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    print(f"Warning: Could not delete temporary file: {str(e)}")
                
                # Extract text and audio from the response
                text_content = response.choices[0].message.content
                audio_data_response = None
                
                # Get the audio data if available
                if hasattr(response.choices[0].message, 'audio') and response.choices[0].message.audio:
                    audio_data_response = base64.b64encode(response.choices[0].message.audio).decode('utf-8')
                
                print(f"INFO: Conversational voice chat successful with {format_ext} format")
                return {
                    "text": text_content,
                    "audio_data": audio_data_response,
                    "format": audio_format
                }
            except Exception as e:
                print(f"ERROR: Failed conversational voice chat with {format_ext} format: {str(e)}")
                last_error = e
                # Continue to the next format
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
        
        # If all formats fail, return the last error
        return {"error": f"Failed conversational voice chat with any supported format: {str(last_error)}"}
    except Exception as e:
        print(f"ERROR: Conversational voice chat failed: {str(e)}")
        return {"error": str(e)}

async def execute_openai_call(model_id: str, message_history: List[Dict[str, Any]], user_input: Union[str, Dict[str, Any]]):
    """ Executes API call to OpenAI using server-side API key """
    openai_api_key = get_api_key("openai")
    if not openai_api_key:
        print("ERROR: OpenAI API key not found in configuration.")
        return { "role": "assistant", "content": "Error: Server API key not configured.", "type": "text" }

    # Format previous messages
    formatted_messages = []
    for msg in message_history:
        if not isinstance(msg, dict) or "role" not in msg or "content" not in msg or msg["role"] not in ["user", "assistant", "system"]:
            continue
            
        # Handle text messages
        if msg.get("type") == "text" or "type" not in msg:
            formatted_messages.append({"role": msg["role"], "content": msg["content"]})
        # Handle image messages
        elif msg.get("type") == "image" and msg["role"] == "user":
            # Extract base64 image data (remove data:image/jpeg;base64, prefix)
            image_data = msg["content"]
            if isinstance(image_data, str) and image_data.startswith('data:'):
                # Extract the content type and base64 data
                content_parts = image_data.split(';base64,')
                if len(content_parts) == 2:
                    image_content = [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_data
                            }
                        }
                    ]
                    
                    # Add caption if available
                    if msg.get("caption"):
                        image_content.append({"type": "text", "text": msg["caption"]})
                    
                    formatted_messages.append({"role": "user", "content": image_content})
        # Handle file messages (non-image attachments)
        elif msg.get("type") == "file" and msg["role"] == "user":
            file_content = msg.get("content", "")
            file_type = msg.get("filetype", "")
            
            # Try to extract text from the file
            success, extracted_text = process_file_content(file_content, file_type)
            
            if success:
                # Use the extracted text
                file_info = f"File content from {msg.get('filename', 'unnamed_file')}:\n\n{extracted_text}"
            else:
                # Fallback to just showing file metadata
                file_info = f"File attached: {msg.get('filename', 'unnamed_file')} ({(msg.get('filesize', 0) / 1024):.1f} KB, type: {file_type})\n\n{extracted_text}"
            
            # Add caption if available
            if msg.get("caption"):
                file_info += f"\n\nUser message: {msg['caption']}"
                
            formatted_messages.append({"role": "user", "content": file_info})
    
    # Add the current user input
    if isinstance(user_input, str):
        # Text input
        formatted_messages.append({"role": "user", "content": user_input})
    elif isinstance(user_input, dict):
        if user_input.get("type") == "image":
            # Image input
            image_data = user_input.get("content", "")
            if isinstance(image_data, str) and image_data.startswith('data:'):
                image_content = [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_data
                        }
                    }
                ]
                
                # Add caption if available
                if user_input.get("caption"):
                    image_content.append({"type": "text", "text": user_input["caption"]})
                    
                formatted_messages.append({"role": "user", "content": image_content})
        elif user_input.get("type") == "file":
            # File input (non-image)
            file_content = user_input.get("content", "")
            file_type = user_input.get("filetype", "")
            
            # Try to extract text from the file
            success, extracted_text = process_file_content(file_content, file_type)
            
            if success:
                # Use the extracted text
                file_info = f"File content from {user_input.get('filename', 'unnamed_file')}:\n\n{extracted_text}"
            else:
                # Fallback to just showing file metadata
                file_info = f"File attached: {user_input.get('filename', 'unnamed_file')} ({(user_input.get('filesize', 0) / 1024):.1f} KB, type: {file_type})\n\n{extracted_text}"
            
            # Add caption if available
            if user_input.get("caption"):
                file_info += f"\n\nUser message: {user_input['caption']}"
                
            formatted_messages.append({"role": "user", "content": file_info})

    try:
        client = openai.AsyncOpenAI(api_key=openai_api_key)
        response = await client.chat.completions.create(
            model=model_id, messages=formatted_messages, temperature=0.7
        )
        return { "role": "assistant", "content": response.choices[0].message.content, "type": "text" }
    except openai.AuthenticationError:
        print("ERROR: OpenAI Authentication Failed.")
        return { "role": "assistant", "content": "Authentication Error.", "type": "text" }
    except openai.RateLimitError:
         print("ERROR: OpenAI Rate Limit Exceeded.")
         return { "role": "assistant", "content": "AI Service busy.", "type": "text" }
    except openai.APIConnectionError as e:
        print(f"ERROR: OpenAI Connection Error: {e}")
        return { "role": "assistant", "content": "Connection Error.", "type": "text" }
    except Exception as e:
        print(f"ERROR: Unexpected error in API call: {str(e)}")
        return { "role": "assistant", "content": f"Error: {str(e)}", "type": "text" }
