# backend/api_calls.py
import os
import openai
import base64
from typing import Dict, List, Any, Optional, Union
from config_utils import get_api_key

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
    
    # Add the current user input
    if isinstance(user_input, str):
        # Text input
        formatted_messages.append({"role": "user", "content": user_input})
    elif isinstance(user_input, dict) and user_input.get("type") == "image":
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
