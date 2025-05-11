# app/models/message.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    AUDIO = "audio"
    SYSTEM = "system"
    AUDIO_RESPONSE = "audio_response"
    REALTIME_AUDIO = "realtime_audio"

class Message(BaseModel):
    """Model representing a message in the chat."""
    role: str
    content: str
    type: MessageType = MessageType.TEXT
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Optional fields for different message types
    caption: Optional[str] = None
    
    # Image-specific fields
    image_url: Optional[str] = None
    
    # File-specific fields
    filename: Optional[str] = None
    filetype: Optional[str] = None
    filesize: Optional[int] = None
    
    # Audio-specific fields
    audio_data: Optional[str] = None
    audio_format: Optional[str] = None

    class Config:
        use_enum_values = True

class MessageHistory(BaseModel):
    """Model representing a conversation history."""
    client_id: str
    messages: List[Message] = []
