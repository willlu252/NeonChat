# backend/api_calls.py
import os
import openai
from typing import Dict, List, Any
from config_utils import get_api_key

async def execute_openai_call(model_id: str, message_history: List[Dict[str, Any]], user_input: str):
    """ Executes API call to OpenAI using server-side API key """
    openai_api_key = get_api_key("openai")
    if not openai_api_key:
        print("ERROR: OpenAI API key not found in configuration.")
        return { "role": "assistant", "content": "Error: Server API key not configured.", "type": "text" }

    formatted_messages = [{"role": msg["role"], "content": msg["content"]}
                          for msg in message_history
                          if isinstance(msg, dict) and "role" in msg and "content" in msg and msg["role"] in ["user", "assistant", "system"]]
    formatted_messages.append({"role": "user", "content": user_input})

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
