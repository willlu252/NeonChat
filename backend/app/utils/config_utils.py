# app/utils/config_utils.py
import os
from dotenv import load_dotenv
import json
from typing import Dict, Any, Optional

# Load environment variables from .env file
load_dotenv()

def get_api_key(provider: str = "openai") -> Optional[str]:
    """
    Get API key for the specified provider from environment variables.
    
    Args:
        provider: The API provider (e.g., "openai", "anthropic", "google")
        
    Returns:
        The API key if found, None otherwise
    """
    if provider.lower() == "openai":
        return os.environ.get("OPENAI_API_KEY")
    elif provider.lower() == "anthropic":
        return os.environ.get("ANTHROPIC_API_KEY")
    elif provider.lower() == "google":
        return os.environ.get("GOOGLE_API_KEY")
    return None

def get_config() -> Dict[str, Any]:
    """
    Get application configuration from environment variables and config files.
    
    Returns:
        Dictionary containing configuration values
    """
    config = {
        "api_keys": {
            "openai": get_api_key("openai"),
            "anthropic": get_api_key("anthropic"),
            "google": get_api_key("google")
        },
        "server": {
            "host": os.environ.get("HOST", "0.0.0.0"),
            "port": int(os.environ.get("PORT", "8000")),
            "debug": os.environ.get("DEBUG", "False").lower() in ("true", "1", "t")
        },
        "models": {
            "default": os.environ.get("DEFAULT_MODEL", "gpt-4o-mini")
        }
    }
    
    return config

def save_example_env_file(path: str = ".env.example") -> None:
    """
    Create an example .env file with placeholders for required environment variables.
    This is useful for new developers setting up the project.
    
    Args:
        path: Path to save the example file
    """
    example_content = """# API Keys - Replace with your actual keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Model Configuration
DEFAULT_MODEL=gpt-4o-mini
"""
    
    with open(path, "w") as f:
        f.write(example_content)
    
    print(f"Example environment file created at {path}")

if __name__ == "__main__":
    # If this file is run directly, create an example .env file
    save_example_env_file()
    
    # Print current configuration (with API keys masked)
    config = get_config()
    for provider, key in config["api_keys"].items():
        if key:
            config["api_keys"][provider] = f"{key[:5]}...{key[-5:]}" if len(key) > 10 else "***"
        else:
            config["api_keys"][provider] = "Not set"
    
    print(json.dumps(config, indent=2))
