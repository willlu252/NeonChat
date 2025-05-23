# NeonChat - Claude Instructions

## Project Overview
NeonChat is a web-based chat application that provides a flexible interface for interacting with various AI models. The project has a Python FastAPI backend and a Vite-powered frontend with vanilla JavaScript.

## Architecture
- **Backend**: FastAPI with modular architecture
  - Entry point: `backend/main.py`
  - Core app: `backend/app/` with API routes, services, models, utils
  - WebSocket communication for real-time chat
  - HTTP routes for other features
- **Frontend**: Vanilla JS/HTML/CSS with Vite build tools
  - Main files: `frontend/static/index.html`, `frontend/static/js/app.js`
  - Styling: `frontend/static/css/styles.css` (primary) + Tailwind CSS utilities

## Key Commands

### Development
```bash
# Backend (from project root)
cd backend && python main.py

# Frontend development server (from project root)  
cd frontend && npm run dev

# Frontend build (from project root)
cd frontend && npm run build
```

### Dependencies
```bash
# Backend dependencies
pip install -r backend/requirements.txt

# Frontend dependencies  
cd frontend && npm install
```

## Current Features
- Text chat with multiple AI providers (OpenAI, Anthropic, Google AI, DeepSeek, Perplexity)
- Image generation via DALL-E 3
- File/image upload and processing
- WebSocket real-time communication
- Settings management with secure API key storage
- Chat history in local storage
- Markdown rendering for responses

## Development Focus
1. **Modular Architecture**: Clean separation between API, services, models, and utilities
2. **Security**: API keys via .env files (backend) or local storage (frontend)
3. **Enhanced AI Capabilities**: Flexible architecture for integrating additional AI providers

## File Structure Notes
- WebSocket handlers: `backend/app/api/ws/` (text_handler.py, image_handler.py, file_handler.py)
- Business logic: `backend/app/services/`
- Configuration: `backend/app/utils/config_utils.py`
- Frontend communication: WebSockets for chat, HTTP for other features

## Testing & Quality
- Run lint/typecheck commands when available (check package.json scripts)
- Test WebSocket connections and API endpoints
- Verify frontend-backend communication

## Important Notes
- Voice features have been completely removed
- ffmpeg directory can be safely deleted
- Focus on text-based interactions and AI model integrations
- Currently integrated with Claude 3.7 Sonnet via Anthropic API