# app/services/message_service.py
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from ..models.message import Message, MessageHistory, MessageType
from ..utils.config_utils import get_config

class MessageService:
    """Service for handling message operations."""
    
    def __init__(self):
        self.message_histories: Dict[str, List[Dict[str, Any]]] = {}
        self.config = get_config()
    
    def add_message(self, client_id: str, message: Dict[str, Any]) -> None:
        """
        Add a message to a client's history.
        
        Args:
            client_id: The client's unique identifier
            message: The message to add
        """
        if client_id not in self.message_histories:
            self.message_histories[client_id] = []
        
        # Ensure the message has a timestamp
        if 'timestamp' not in message:
            message['timestamp'] = datetime.now().isoformat()
        
        self.message_histories[client_id].append(message)
    
    def get_message_history(self, client_id: str) -> List[Dict[str, Any]]:
        """
        Get a client's message history.
        
        Args:
            client_id: The client's unique identifier
            
        Returns:
            The client's message history
        """
        return self.message_histories.get(client_id, [])
    
    def clear_message_history(self, client_id: str) -> None:
        """
        Clear a client's message history.
        
        Args:
            client_id: The client's unique identifier
        """
        if client_id in self.message_histories:
            self.message_histories[client_id] = []
    
    def create_user_message(self, content: str, message_type: str = "text", **kwargs) -> Dict[str, Any]:
        """
        Create a user message object.
        
        Args:
            content: The message content
            message_type: The type of message (text, image, file, audio)
            **kwargs: Additional message properties
            
        Returns:
            The message object
        """
        message = {
            'role': 'user',
            'content': content,
            'type': message_type,
            'timestamp': datetime.now().isoformat()
        }
        
        # Add any additional properties
        for key, value in kwargs.items():
            message[key] = value
        
        return message
    
    def create_assistant_message(self, content: str, message_type: str = "text", **kwargs) -> Dict[str, Any]:
        """
        Create an assistant message object.
        
        Args:
            content: The message content
            message_type: The type of message (text, image, file, audio)
            **kwargs: Additional message properties
            
        Returns:
            The message object
        """
        message = {
            'role': 'assistant',
            'content': content,
            'type': message_type,
            'timestamp': datetime.now().isoformat()
        }
        
        # Add any additional properties
        for key, value in kwargs.items():
            message[key] = value
        
        return message
        
    def create_system_message(self, content: str) -> Dict[str, Any]:
        """
        Create a system message object.
        
        Args:
            content: The message content
            
        Returns:
            The message object
        """
        return {
            'role': 'system',
            'content': content,
            'type': 'system',
            'timestamp': datetime.now().isoformat()
        }

# Create a global service instance
message_service = MessageService()
