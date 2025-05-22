# constants.py
# Stores constants for Claude Chat app

APP_TITLE = "Claude Chat"
APP_DESCRIPTION = "A fast, TRON-themed chat interface for Anthropic's Claude 3.7 Sonnet."

# Claude model definition
CLAUDE_MODEL = {
    "name": "Claude 3.7 Sonnet",
    "provider": "Anthropic",
    "id": "claude-3-7-sonnet-20250219",
    "type": "text",
    "capabilities": "Anthropic's most intelligent model with top-tier benchmark results in reasoning, coding, multilingual tasks, and vision.",
    "context_length": 200000,
    "pricing": {
        "input": "$3.00 per 1M tokens",
        "output": "$15.00 per 1M tokens"
    }
}