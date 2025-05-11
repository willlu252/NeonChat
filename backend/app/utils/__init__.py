# app/utils/__init__.py
from .config_utils import get_api_key, get_config, save_example_env_file
from .file_utils import extract_text_from_docx, process_file_content
from .audio_utils import (
    FFMPEG_PATH, FFMPEG_AVAILABLE, 
    convert_audio_format, 
    decode_base64_audio, 
    encode_audio_to_base64
)