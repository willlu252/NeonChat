# NeonChat Project Overview

## 1. Project Goal

NeonChat is a web-based chat application designed to provide a flexible interface for interacting with various AI models and services. The current development phase focuses on removing legacy voice functionalities and integrating deeply with Abacus.ai for enhanced AI capabilities, including image generation, advanced search, diary management, and model selection. The application aims to maintain its existing direct ChatGPT API interaction while expanding its feature set through Abacus.ai.

## 2. Core Technologies

*   **Frontend:** Vanilla JavaScript, HTML5, CSS3 (Tailwind CSS utility classes are present in config, but primary styling is via `styles.css` and `input.css`)
*   **Backend:** Python with FastAPI framework
*   **Communication:** WebSockets for real-time chat; REST APIs for other features.
*   **AI Services:**
    *   OpenAI API (direct integration for general chat, DALL-E 3 for image generation)
    *   Abacus.ai (planned integration for custom agents and specialized AI tasks)

## 3. Project Structure

```
NeonChat-main/
├── .git/                     # Git repository files
├── .venv/                    # Python virtual environment (typical location)
├── backend/                  # Python FastAPI backend
│   ├── app/                  # Core application module
│   │   ├── api/              # API endpoint definitions
│   │   │   ├── routes/       # Route handlers
│   │   │   │   ├── abacus_routes.py  # Placeholder/actual routes for Abacus.ai features
│   │   │   │   ├── http.py     # General HTTP routes
│   │   │   │   ├── ws.py       # WebSocket endpoint logic
│   │   │   │   └── __init__.py
│   │   │   ├── ws/           # WebSocket message handlers
│   │   │   │   ├── file_handler.py
│   │   │   │   ├── image_handler.py
│   │   │   │   ├── text_handler.py
│   │   │   │   └── __init__.py
│   │   │   └── __init__.py   # Sets up API routes (HTTP & WebSocket)
│   │   ├── models/           # Pydantic models (if any, currently empty or not primary focus)
│   │   ├── services/         # Business logic (e.g., message_service.py)
│   │   ├── utils/            # Utility functions (e.g., config_utils.py)
│   │   └── __init__.py       # FastAPI app creation (create_app function)
│   ├── tests/                # Backend tests
│   ├── api_calls.py          # Handles direct calls to OpenAI (chat, DALL-E)
│   ├── config_utils.py       # Utilities for configuration management
│   ├── constants.py          # Project-wide constants
│   ├── file_utils.py         # Utilities for file processing
│   ├── main.py               # Backend entry point (runs Uvicorn server)
│   ├── projects_utils.py     # Utilities for project management features
│   ├── requirements.txt      # Python backend dependencies
│   └── ui_components.py      # Potentially for server-side UI components or dynamic content
├── frontend/                 # Frontend application (Vanilla JS, HTML, CSS)
│   ├── dist/                 # Vite build output directory (if `vite build` is run)
│   ├── node_modules/         # Node.js dependencies for frontend development tools
│   ├── src/                  # Original source files (before Vite processing, if applicable)
│   │   └── input.css         # Additional Tailwind directives/custom CSS
│   ├── static/               # Static assets served directly
│   │   ├── css/
│   │   │   ├── abacus-integration.css # Styles for Abacus.ai features
│   │   │   └── styles.css           # Main application styles
│   │   ├── js/
│   │   │   ├── abacus-integration.js # JS for Abacus.ai UI interaction
│   │   │   └── app.js                # Main frontend JavaScript logic
│   │   ├── index.html        # Main HTML file for the single-page application
│   │   └── sidebar.html      # HTML snippet for the sidebar (potentially loaded by JS)
│   ├── .gitignore
│   ├── package.json          # Frontend dependencies and scripts (e.g., Vite)
│   ├── package-lock.json
│   ├── postcss.config.js     # PostCSS configuration (used by Tailwind)
│   ├── tailwind.config.js    # Tailwind CSS configuration
│   └── vite.config.js        # Vite build tool configuration
├── ABACUS_INTEGRATION.md     # Documentation for Abacus.ai integration details
├── NEONCHAT_ROADMAP.md       # Project roadmap and phased development plan
├── README.md                 # General project README
└── requirements.txt          # Duplicate or older root-level requirements (backend/requirements.txt is primary)
```
*(Note: `ffmpeg/` and `ffmpeg.zip` were identified as likely unused and recommended for manual deletion).*

## 4. How the App Works

### 4.1. Frontend

*   **Rendering:** The frontend is a single-page application (SPA) with `frontend/static/index.html` as the main entry point.
*   **JavaScript Logic (`frontend/static/js/app.js`):**
    *   Handles DOM manipulation to display chat messages, update UI elements.
    *   Manages different views (Chat, Settings, Projects, Models Info, and planned Abacus feature views like Image Generation, Diary, Search) by showing/hiding relevant HTML sections.
    *   Manages user input from the chat text area.
    *   Initiates WebSocket connection to the backend.
    *   Sends user messages and commands (e.g., image generation requests) to the backend via WebSocket.
    *   Receives messages and updates from the backend via WebSocket and displays them.
    *   Handles client-side settings and interactions with UI elements like the sidebar and modals.
*   **Abacus.ai UI (`frontend/static/js/abacus-integration.js` & `css/abacus-integration.css`):**
    *   Contains JavaScript and CSS specifically for the UI elements related to the planned Abacus.ai features (Image Generation, Search, Diary). These will interact with the backend APIs that proxy requests to Abacus.ai.
*   **Styling:** Primarily done through `frontend/static/css/styles.css`. Tailwind CSS is configured (`tailwind.config.js`, `postcss.config.js`, `frontend/src/input.css`), suggesting its utility classes can be used or are processed into the main stylesheets.

### 4.2. Backend (FastAPI)

*   **Entry Point (`backend/main.py`):** Initializes and runs the FastAPI application using Uvicorn.
*   **App Creation (`backend/app/__init__.py`):** The `create_app` function sets up the FastAPI instance, including CORS middleware, static file serving (for the frontend), and API routes.
*   **API Routes (`backend/app/api/`):**
    *   **HTTP Routes (`http.py`, `abacus_routes.py`):** Handle standard HTTP requests. The `abacus_routes.py` will contain endpoints like `/api/generate-image`, `/api/search`, `/api/save-diary`, `/api/chat-abacus` that will proxy requests to the respective Abacus.ai agents (as outlined in `NEONCHAT_ROADMAP.md` and `ABACUS_INTEGRATION.md`).
    *   **WebSocket Endpoint (`ws.py`):** Manages persistent WebSocket connections at `/ws`. It receives JSON messages from the client.
        *   **Message Handling (`backend/app/api/ws/` handlers):** Based on the `type` field in the received JSON message, the `websocket_endpoint` routes the data to specific handlers (`text_handler.py`, `image_handler.py`, `file_handler.py`). These handlers process the message and may interact with services or directly call external APIs (like OpenAI).
*   **External API Calls (`backend/api_calls.py`):**
    *   Contains functions to directly interact with the OpenAI API for chat completions (`execute_openai_call`) and DALL-E 3 image generation (`generate_image`).
    *   This module is where API keys are retrieved (via `config_utils.py`) and used.
*   **Services (e.g., `backend/app/services/message_service.py`):** Intended to encapsulate business logic, such as formatting messages or orchestrating calls to different AI providers.
*   **Configuration (`backend/app/utils/config_utils.py`, `.env` file expected):** Manages API keys and other configuration settings, likely loaded from an `.env` file.

### 4.3. Frontend-Backend Communication

*   **Primary Channel:** WebSockets are used for real-time, bidirectional communication between the frontend (`app.js`) and the backend (`ws.py`). This is used for sending chat messages, user commands, and receiving AI responses and updates.
*   **HTTP for Abacus.ai Features:** The UI for Abacus.ai features (e.g., Image Generation form) will make standard HTTP POST requests (e.g., to `/api/generate-image`) to the backend. The backend will then use the Abacus.ai Python SDK to interact with the Abacus.ai platform.

## 5. Abacus.ai Integration (Planned)

As detailed in `NEONCHAT_ROADMAP.md` and `ABACUS_INTEGRATION.md`:
*   The project will integrate Abacus.ai for several key AI tasks by creating specific agents within the Abacus.ai platform.
*   **Backend Endpoints:** Dedicated FastAPI endpoints will be developed to serve as a bridge between NeonChat and these Abacus.ai agents:
    *   `/api/generate-image`: For image generation.
    *   `/api/search`: For normal and deep research searches.
    *   `/api/save-diary`: For saving diary entries.
    *   `/api/chat-abacus`: For interacting with generic LLM agents or specific models hosted on Abacus.ai.
*   **Frontend UI:** New UI components are planned (and some HTML/JS placeholders exist) for interacting with these features (e.g., forms for image generation parameters, search type selection).
*   **Context Management:** Strategies will be implemented to maintain conversational context when interacting with Abacus.ai agents.

## 6. Current State & Next Steps (Post Voice Removal)

*   All voice-related UI elements, JavaScript functions, CSS, and backend Python code (including dependencies like `pydub` and specific API handlers) have been removed.
*   The application supports text and file/image-based chat via OpenAI.
*   The groundwork for Abacus.ai integration is present in terms of documentation and some frontend placeholders.
*   Next steps involve fully implementing the backend API endpoints and frontend UI for the Abacus.ai features as outlined in the roadmap.

This overview should provide comprehensive context for future development and AI interactions. 