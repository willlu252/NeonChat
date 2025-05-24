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
- **Multi-AI Chat**: Text chat with multiple AI providers (OpenAI, Anthropic, Google AI, DeepSeek, Perplexity)
- **Image Generation**: DALL-E 3 integration for image creation
- **File Processing**: File/image upload and processing capabilities
- **Project Workspaces**: Complete project management system with:
  - Project creation, editing, and deletion
  - File upload and management per project
  - System instructions/prompts for project-specific AI behavior
  - Dedicated chat interface with project context
  - Local storage persistence
- **Journal System**: Comprehensive journaling with metrics tracking
- **Real-time Communication**: WebSocket-based streaming responses
- **Settings Management**: Secure API key storage and configuration
- **Chat History**: Persistent chat history in local storage
- **Markdown Support**: Full markdown rendering for AI responses

## Development Focus
1. **Modular Architecture**: Clean separation between API, services, models, and utilities
2. **Security**: API keys via .env files (backend) or local storage (frontend)
3. **Enhanced AI Capabilities**: Flexible architecture for integrating additional AI providers

## File Structure Notes
- **Backend Structure**:
  - WebSocket handlers: `backend/app/api/ws/` (text_handler.py, image_handler.py, file_handler.py)
  - Business logic: `backend/app/services/`
  - Configuration: `backend/app/utils/config_utils.py`
  - API routes: `backend/app/api/routes/` (auth.py, journal.py, metrics.py, etc.)
- **Frontend Structure**:
  - Main app: `frontend/static/js/app.js` (core application logic)
  - Projects: `frontend/static/js/projects.js` (project management system)
  - Journal: `frontend/static/js/journal-ui.js`, `frontend/static/js/journal-api.js`
  - Metrics: `frontend/static/js/metrics-ui.js`
  - Styling: `frontend/static/css/styles.css` (Tron-themed UI)
  - Authentication: `frontend/static/js/auth.js` (Firebase integration)
- **Communication**: WebSockets for chat, HTTP for data management

## Testing & Quality
- Run lint/typecheck commands when available (check package.json scripts)
- Test WebSocket connections and API endpoints
- Verify frontend-backend communication

## UI/UX Design Philosophy
- **Fixed Layout**: No vertical page scrolling - all scrolling contained within specific containers
- **Tron Theme**: Neon blue/pink cyberpunk aesthetic with dark backgrounds
- **Responsive Sidebars**: 
  - Main navigation sidebar (25% width, always visible)
  - Content areas use 80% width (default) or 90% width (journal/projects)
  - Project workspace: Left info (250px) + Main chat (flexible) + Right tools (320px)
- **Consistent Chat UX**: Fixed input areas, scrollable canvas, same interaction patterns

## Important Notes
- Voice features have been completely removed
- ffmpeg directory can be safely deleted  
- Focus on text-based interactions and AI model integrations
- Currently integrated with Claude 3.7 Sonnet via Anthropic API
- Projects system uses local storage (ready for backend integration)
- Journal system includes comprehensive metrics and AI interactions