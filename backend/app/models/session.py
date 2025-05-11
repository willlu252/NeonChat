# app/models/session.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

class Session(BaseModel):
    """Model representing a user session."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.now)
    last_active: datetime = Field(default_factory=datetime.now)
    
    # Settings and preferences
    model_id: Optional[str] = None
    tts_enabled: bool = False
    tts_voice: str = "alloy"
    tts_speed: float = 1.0
    
    # Realtime conversation settings
    realtime_mode: str = "cheap"  # "cheap" or "complex"
    
    def update_activity(self):
        """Update the last_active timestamp to now."""
        self.last_active = datetime.now()
        
    class Config:
        arbitrary_types_allowed = True
