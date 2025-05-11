# app/services/api_service.py
from typing import Dict, List, Any, Optional, Union
import json
from openai import AsyncOpenAI
from ..utils.config_utils import get_api_key, get_config
from ..utils.file_utils import process_file_content

class ApiService:
    """Service for handling API calls to AI models."""
    
    def __init__(self):
        self.config = get_config()
        self.openai_api_key = get_api_key("openai")
        self.anthropic_api_key = get_api_key("anthropic")
        self.google_api_key = get_api_key("google")
    
    async def execute_openai_call(
        self, 
        model_id: str, 
        message_history: List[Dict[str, Any]], 
        user_input: Union[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Execute an API call to OpenAI ChatGPT models.
        
        Args:
            model_id: The model ID to use
            message_history: Previous conversation history
            user_input: User input (text or structured data)
            
        Returns:
            The AI response
        """
        if not self.openai_api_key:
            return {"role": "assistant", "content": "API key not configured. Please set up your OpenAI API key."}
        
        try:
            # Set up API client
            client = AsyncOpenAI(api_key=self.openai_api_key)
            
            # Prepare messages
            messages = []
            for msg in message_history:
                # Skip messages that aren't compatible with the OpenAI API
                if msg.get('type') in ['system', 'text', 'image_url', 'image']:
                    # Convert our internal message format to OpenAI's format
                    if msg.get('role') in ['user', 'assistant', 'system']:
                        openai_msg = {"role": msg.get('role'), "content": msg.get('content')}
                        
                        # Handle image messages
                        if msg.get('type') == 'image':
                            # For image messages, create a message with text and image
                            openai_msg["content"] = []
                            
                            # Add caption text if available, otherwise use a generic message
                            caption = msg.get('caption', 'Image for analysis')
                            openai_msg["content"].append({"type": "text", "text": caption})
                            
                            # Add the image
                            if 'image_url' in msg:
                                openai_msg["content"].append({
                                    "type": "image_url",
                                    "image_url": {"url": msg['image_url']}
                                })
                        
                        messages.append(openai_msg)
            
            # Add the current user message
            if isinstance(user_input, str):
                # Simple text message
                user_message = {"role": "user", "content": user_input}
                messages.append(user_message)
            else:
                # Complex message (e.g., with images or files)
                if user_input.get('type') == 'image':
                    # Handle image URLs in the content
                    user_message = {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_input.get('caption', 'Image for analysis')},
                            {"type": "image_url", "image_url": {"url": user_input.get('content')}}
                        ]
                    }
                    messages.append(user_message)
                elif user_input.get('type') == 'file':
                    # Process file content
                    success, text = process_file_content(user_input.get('content'), user_input.get('filetype', 'text/plain'))
                    if success:
                        file_message = f"File content: {text}"
                        if 'caption' in user_input:
                            file_message = f"{user_input['caption']}\n\n{file_message}"
                        user_message = {"role": "user", "content": file_message}
                        messages.append(user_message)
                    else:
                        user_message = {"role": "user", "content": f"Error processing file: {text}"}
                        messages.append(user_message)
            
            # Make the API call
            response = await client.chat.completions.create(
                model=model_id,
                messages=messages,
                temperature=0.7,
                max_tokens=4000,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            # Extract and return the response
            response_message = response.choices[0].message
            return {
                "role": "assistant",
                "content": response_message.content,
                "model": model_id,
                "type": "text"
            }
            
        except Exception as e:
            print(f"ERROR: API call failed: {str(e)}")
            return {"role": "assistant", "content": f"Sorry, an error occurred: {str(e)}", "type": "text"}

# Create a global service instance
api_service = ApiService()
