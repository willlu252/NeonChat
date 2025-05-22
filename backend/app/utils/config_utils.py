# app/utils/config_utils.py
import os
from dotenv import load_dotenv
import json
from typing import Dict, Any, Optional

# Load environment variables from .env file
load_dotenv()

def get_api_key(provider: str = "anthropic") -> Optional[str]:
    """
    Get API key for Anthropic Claude from environment variables.
    
    Args:
        provider: The API provider (only "anthropic" supported)
        
    Returns:
        The API key if found, None otherwise
    """
    if provider.lower() == "anthropic":
        return os.environ.get("ANTHROPIC_API_KEY")
    return None

def get_config() -> Dict[str, Any]:
    """
    Get application configuration from environment variables.
    
    Returns:
        Dictionary containing configuration values
    """
    config = {
        "api_keys": {
            "anthropic": get_api_key("anthropic")
        },
        "server": {
            "host": os.environ.get("HOST", "0.0.0.0"),
            "port": int(os.environ.get("PORT", "8000")),
            "debug": os.environ.get("DEBUG", "False").lower() in ("true", "1", "t")
        },
        "models": {
            "default": "claude-3-7-sonnet-20250219"
        }
    }
    
    return config

def save_example_env_file(path: str = ".env.example") -> None:
    """
    Create an example .env file with placeholder for Anthropic API key.
    
    Args:
        path: Path to save the example file
    """
    example_content = """# API Key - Replace with your actual Anthropic API key
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False
"""
    
    with open(path, "w") as f:
        f.write(example_content)
    
    print(f"Example environment file created at {path}")

if __name__ == "__main__":
    # If this file is run directly, create an example .env file
    save_example_env_file()
    
    # Print current configuration (with API key masked)
    config = get_config()
    key = config["api_keys"]["anthropic"]
    if key:
        config["api_keys"]["anthropic"] = f"{key[:5]}...{key[-5:]}" if len(key) > 10 else "***"
    else:
        config["api_keys"]["anthropic"] = "Not set"
    
    print(json.dumps(config, indent=2))