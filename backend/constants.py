# constants.py
# Stores constants like titles and model definitions

APP_TITLE = "Tron AI Chat"
APP_DESCRIPTION = "A TRON-themed chat interface for interacting with various frontier AI models."

# Model definitions dictionary
MODEL_OPTIONS = {
    # --- DeepSeek ---
    "DeepSeek Reasoner (DeepSeek-R1)": {
        "provider": "DeepSeek",
        "id": "deepseek-reasoner",
        "type": "text",
        "capabilities": "Advanced reasoning, mathematical problem-solving, and programming assistance.",
        "context_length": 64000,
        "pricing": {
            "input_cache_miss": "$0.55 per 1M tokens",
            "input_cache_hit": "$0.14 per 1M tokens",
            "output": "$2.19 per 1M tokens"
        }
    },
    
    # --- Anthropic (Claude) ---
    "Claude 3.7 Sonnet": {
        "provider": "Anthropic",
        "id": "claude-3-7-sonnet-20250219",
        "type": "text",
        "capabilities": "Anthropic's most intelligent model with top-tier benchmark results in reasoning, coding, multilingual tasks, and vision.",
        "context_length": 200000,
        "pricing": {
            "input": "$3.00 per 1M tokens",
            "output": "$15.00 per 1M tokens"
        }
    },
    "Claude 3 Opus": {
        "provider": "Anthropic",
        "id": "claude-3-opus-20240229",
        "type": "text",
        "capabilities": "Previously Anthropic's most powerful model, excelling at complex analysis, research, strategic tasks, and long-form content generation.",
        "context_length": 200000,
        "pricing": {
            "input": "$15.00 per 1M tokens",
            "output": "$75.00 per 1M tokens"
        }
    },
    "Claude 3 Sonnet": {
        "provider": "Anthropic",
        "id": "claude-3-sonnet-20240229",
        "type": "text",
        "capabilities": "A balance between intelligence and speed, suitable for enterprise workloads like data processing, RAG, and coding tasks.",
        "context_length": 200000,
        "pricing": {
            "input": "$3.00 per 1M tokens",
            "output": "$15.00 per 1M tokens"
        }
    },
    "Claude 3 Haiku": {
        "provider": "Anthropic",
        "id": "claude-3-haiku-20240307",
        "type": "text",
        "capabilities": "The fastest and most compact model in the original Claude 3 family, designed for near-instant responsiveness.",
        "context_length": 200000,
        "pricing": {
            "input": "$0.25 per 1M tokens",
            "output": "$1.25 per 1M tokens"
        }
    },
    
    # --- Google (Gemini) ---
    "Gemini 1.5 Pro": {
        "provider": "Google",
        "id": "gemini-1.5-pro",
        "type": "text",
        "capabilities": "Google's most capable Gemini 1.5 series model for complex reasoning, multimodal understanding, coding, and tasks requiring high intelligence.",
        "context_length": 2000000,
        "pricing": {
            "input_small": "$1.25 per 1M tokens (≤128k tokens)",
            "input_large": "$2.50 per 1M tokens (>128k tokens)",
            "output_small": "$5.00 per 1M tokens (≤128k tokens)",
            "output_large": "$10.00 per 1M tokens (>128k tokens)"
        }
    },
    "Gemini 1.5 Flash": {
        "provider": "Google",
        "id": "gemini-1.5-flash",
        "type": "text",
        "capabilities": "Optimised for speed and cost-efficiency while maintaining strong multimodal capabilities and a large context window.",
        "context_length": 1000000,
        "pricing": {
            "input_small": "$0.075 per 1M tokens (≤128k tokens)",
            "input_large": "$0.15 per 1M tokens (>128k tokens)",
            "output_small": "$0.30 per 1M tokens (≤128k tokens)",
            "output_large": "$0.60 per 1M tokens (>128k tokens)"
        }
    },
    "Gemini 2.5 Pro (Preview)": {
        "provider": "Google",
        "id": "gemini-2.5-pro-preview-03-25",
        "type": "text",
        "capabilities": "Google's latest preview model with advanced capabilities.",
        "context_length": 2000000,
        "pricing": {
            "input": "$3.50 per 1M tokens",
            "output": "$14.00 per 1M tokens"
        }
    },
    
    # --- Perplexity ---
    "Perplexity Sonar API": {
        "provider": "Perplexity",
        "id": "sonar-medium-online",
        "type": "text",
        "capabilities": "Provides AI-generated answers based on web searches, including citations. Optimised for speed and cost-efficiency.",
        "context_length": 127000,
        "pricing": {
            "input": "$1.00 per 1M tokens",
            "output": "$1.00 per 1M tokens"
        }
    },
    "Perplexity Sonar Pro API": {
        "provider": "Perplexity",
        "id": "sonar-pro-online",
        "type": "text",
        "capabilities": "More capable than the standard Sonar API, better at handling complex queries. Provides more citations.",
        "context_length": 200000,
        "pricing": {
            "input": "$3.00 per 1M tokens",
            "output": "$15.00 per 1M tokens"
        }
    },
    
    # --- OpenAI (GPT) ---
    "GPT-4.1": {
        "provider": "OpenAI",
        "id": "gpt-4.1-2025-04-14",
        "type": "text",
        "capabilities": "OpenAI's latest high-intelligence model iteration, offering strong reasoning and performance.",
        "context_length": 128000,
        "pricing": {
            "input": "$2.00 per 1M tokens",
            "input_cached": "$0.50 per 1M tokens",
            "output": "$8.00 per 1M tokens"
        }
    },
    "GPT-4.1 mini": {
        "provider": "OpenAI",
        "id": "gpt-4.1-mini-2025-04-14",
        "type": "text",
        "capabilities": "A faster, more cost-effective version of GPT-4.1, balancing capability with efficiency.",
        "context_length": 128000,
        "pricing": {
            "input": "$0.40 per 1M tokens",
            "input_cached": "$0.10 per 1M tokens",
            "output": "$1.60 per 1M tokens"
        }
    },
    "GPT-4o": {
        "provider": "OpenAI",
        "id": "gpt-4o-2024-08-06",
        "type": "text",
        "capabilities": "Highly capable flagship model with strong performance across text, reasoning, coding, and native multimodality (audio, vision, text).",
        "context_length": 128000,
        "pricing": {
            "input": "$2.50 per 1M tokens",
            "input_cached": "$1.25 per 1M tokens",
            "output": "$10.00 per 1M tokens"
        }
    },
    "GPT-4o mini": {
        "provider": "OpenAI",
        "id": "gpt-4o-mini-2024-07-18",
        "type": "text",
        "capabilities": "OpenAI's most affordable and fastest model as of its release. Designed to offer strong intelligence for its cost.",
        "context_length": 128000,
        "pricing": {
            "input": "$0.15 per 1M tokens",
            "input_cached": "$0.075 per 1M tokens",
            "output": "$0.60 per 1M tokens"
        }
    },
    "GPT-4": {
        "provider": "OpenAI",
        "id": "gpt-4",
        "type": "text",
        "capabilities": "Advanced reasoning, coding, instruction following.",
        "context_length": 8192,
        "pricing": {
            "input": "$30.00 per 1M tokens",
            "output": "$60.00 per 1M tokens"
        }
    },
    "GPT-3.5 Turbo": {
        "provider": "OpenAI",
        "id": "gpt-3.5-turbo",
        "type": "text",
        "capabilities": "Fast, efficient text generation and conversation.",
        "context_length": 16385,
        "pricing": {
            "input": "$0.50 per 1M tokens",
            "output": "$1.50 per 1M tokens"
        }
    }
}
