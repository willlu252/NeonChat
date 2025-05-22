# app/services/api_service.py
from typing import Dict, List, Any, Optional, Union, AsyncIterator
import json
import httpx
from ..utils.config_utils import get_api_key
from ..utils.file_utils import process_file_content

class ApiService:
    """Service for handling API calls to Claude models."""
    
    def __init__(self):
        self.anthropic_api_key = get_api_key("anthropic")
    
    async def execute_claude_call_streaming(
        self, 
        message_history: List[Dict[str, Any]], 
        user_input: Union[str, Dict[str, Any]]
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Execute a streaming API call to Anthropic Claude 3.7 Sonnet.
        
        Args:
            message_history: Previous conversation history
            user_input: User input (text or structured data)
            
        Yields:
            Streaming response chunks
        """
        if not self.anthropic_api_key:
            yield {
                "role": "assistant", 
                "content": "Anthropic API key not configured. Please set up your Anthropic API key in the .env file.",
                "type": "error",
                "done": True
            }
            return
        
        try:
            # Use Claude 3.7 Sonnet model
            model_id = "claude-3-7-sonnet-20250219"

            # Prepare messages in Anthropic format
            messages = []
            for msg in message_history:
                if msg.get('role') in ['user', 'assistant'] and 'content' in msg:
                    messages.append({
                        "role": msg.get('role'),
                        "content": msg.get('content')
                    })
            
            # Add current user message
            if isinstance(user_input, str):
                messages.append({"role": "user", "content": user_input})
            elif isinstance(user_input, dict):
                if user_input.get('type') == 'file':
                    # Process file content
                    success, text = process_file_content(user_input.get('content'), user_input.get('filetype', 'text/plain'))
                    if success:
                        file_message = f"File content: {text}"
                        if 'caption' in user_input:
                            file_message = f"{user_input['caption']}\n\n{file_message}"
                        messages.append({"role": "user", "content": file_message})
                    else:
                        yield {
                            "role": "assistant", 
                            "content": f"Error processing file: {text}",
                            "type": "error",
                            "done": True
                        }
                        return
                else:
                    # Handle other message types
                    content = user_input.get('content', '')
                    if user_input.get('caption'):
                        content = f"{user_input['caption']}\n\n{content}"
                    messages.append({"role": "user", "content": content})
            
            # Construct the API payload with streaming enabled
            payload = {
                "model": model_id,
                "messages": messages,
                "max_tokens": 4096,
                "temperature": 0.7,
                "stream": True  # Enable streaming
            }
            
            # Call Anthropic API with streaming
            headers = {
                "x-api-key": self.anthropic_api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    "https://api.anthropic.com/v1/messages",
                    json=payload,
                    headers=headers,
                    timeout=60.0
                ) as response:
                    
                    if response.status_code != 200:
                        yield {
                            "role": "assistant", 
                            "content": f"Sorry, an error occurred with the Claude API: {response.status_code}",
                            "type": "error",
                            "done": True
                        }
                        return
                    
                    # Process streaming response
                    async for line in response.aiter_lines():
                        if line.startswith('data: '):
                            data = line[6:]  # Remove 'data: ' prefix
                            
                            if data == '[DONE]':
                                yield {
                                    "role": "assistant",
                                    "content": "",
                                    "model": model_id,
                                    "type": "text",
                                    "done": True
                                }
                                return
                            
                            try:
                                chunk = json.loads(data)
                                
                                # Handle different event types
                                if chunk.get('type') == 'content_block_delta':
                                    delta = chunk.get('delta', {})
                                    if delta.get('type') == 'text_delta':
                                        text = delta.get('text', '')
                                        if text:
                                            yield {
                                                "role": "assistant",
                                                "content": text,
                                                "model": model_id,
                                                "type": "text_chunk",
                                                "done": False
                                            }
                                
                                elif chunk.get('type') == 'message_stop':
                                    yield {
                                        "role": "assistant",
                                        "content": "",
                                        "model": model_id,
                                        "type": "text",
                                        "done": True
                                    }
                                    return
                                    
                            except json.JSONDecodeError:
                                continue  # Skip malformed JSON
                
        except Exception as e:
            print(f"ERROR: Claude streaming API call failed: {str(e)}")
            yield {
                "role": "assistant", 
                "content": f"Sorry, an error occurred: {str(e)}",
                "type": "error",
                "done": True
            }

    async def execute_claude_call(
        self, 
        message_history: List[Dict[str, Any]], 
        user_input: Union[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Execute a non-streaming API call to Anthropic Claude 3.7 Sonnet.
        This is kept for backward compatibility, but streaming is preferred.
        """
        # Collect all streaming chunks into a single response
        full_content = ""
        async for chunk in self.execute_claude_call_streaming(message_history, user_input):
            if chunk.get("type") == "text_chunk":
                full_content += chunk.get("content", "")
            elif chunk.get("done"):
                break
        
        return {
            "role": "assistant",
            "content": full_content,
            "model": "claude-3-7-sonnet-20250219",
            "type": "text"
        }

# Create a global service instance
api_service = ApiService()