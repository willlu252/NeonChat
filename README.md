# NeonChat

## Description

NeonChat is a web-based chat application designed as a wrapper to interact with various Large Language Models (LLMs). Select your preferred model provider, configure your API key via the secure settings interface, and start chatting.

This project serves as a foundation for experimenting with different AI models and is intended to be expanded with more features over time.

## Features

* Chat interface supporting various AI models.
* Currently supported providers: OpenAI, Google AI, Anthropic, DeepSeek, Perplexity.
* Real-time interaction using WebSockets.
* Conversation debugging features with audio transcription and real-time voice chat.
* Settings page to manage API keys (stored securely in your browser's local storage).
* Model selection capabilities.
* Renders model responses as Markdown.
* Secure server-side API key management using environment variables.
* Chat history saved in local storage.

## Technology Stack

* **Backend:**
    * Python 3.x
    * FastAPI (Web framework)
    * Uvicorn (ASGI server)
    * OpenAI Python Library
    * Anthropic Python Library
    * Google Generative AI Library
    * Requests
    * python-dotenv (Environment variable management)
    * Modular architecture with separation of concerns
    * *(Other dependencies listed in `backend/requirements.txt`)*
* **Frontend:**
    * Vite (Build tool / Dev server)
    * Alpine.js (Minimal JavaScript framework)
    * HTMX (AJAX/WebSocket integration in HTML)
    * Tailwind CSS (Utility-first CSS framework)
    * Marked.js (Markdown parser)
    * FilePond (File uploads - potentially for future features)
    * JavaScript
    * HTML / CSS
    * *(Dependencies listed in `package.json`)*

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

* Python (version 3.8 or higher recommended)
* `pip` (Python package installer)
* Node.js (version 14 or higher) and `npm` (or `yarn`)
* For image processing: Tesseract OCR (required for pytesseract)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/willlu252/NeonChat.git
    ```
2.  **Navigate to the project directory:**
    ```bash
    cd NeonChat
    ```
3.  **Install backend dependencies:**
    * It's recommended to use a virtual environment:
        ```bash
        python -m venv venv
        # Activate the virtual environment
        # Windows (Git Bash/MINGW64):
        source venv/Scripts/activate 
        # Windows (Command Prompt):
        # .\venv\Scripts\activate 
        # macOS/Linux:
        # source venv/bin/activate 
        ```
    * Install the required packages:
        ```bash
        pip install -r backend/requirements.txt 
        ```
        
    * Note: If you encounter any dependency issues, you can also try the root requirements.txt:
        ```bash
        pip install -r requirements.txt
        ```

4.  **Install frontend dependencies:**
    * *(Run these commands in the root directory)*
        ```bash
        cd frontend
        npm install 
        ```
        *(or `yarn install` if you use Yarn)*

5.  **Development Mode (Optional):**
    * To run the frontend in development mode:
        ```bash
        cd frontend
        npm run dev
        ```
    * This will start the Vite development server on port 5173

6.  **Build the frontend:**
    * *(This command uses the build script defined in your `package.json`)*
        ```bash
        cd frontend
        npm run build
        ```
        *(or `yarn build`)*
        This will generate the static files in the `frontend/dist` directory, which the FastAPI backend serves.

### Configuration

#### API Keys Configuration

There are two ways to configure API keys for the application:

1. **Environment Variables (Recommended for Production):**
   * Create a `.env` file in the `backend` directory (this file is gitignored and will not be pushed to GitHub)
   * Add your API keys to this file:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     ANTHROPIC_API_KEY=your_anthropic_api_key_here
     GOOGLE_API_KEY=your_google_api_key_here
     ```
   * The application will automatically load these environment variables when it starts

2. **Settings UI (Alternative for Development):**
   * Run the application (see next step)
   * Open the application in your web browser (`http://localhost:8000`)
   * Navigate to the 'Settings' page using the application's UI
   * Enter your API keys for the desired providers. These keys are stored only in your browser's local storage for security.

#### Server Configuration

You can also configure server settings in the `.env` file:

```
HOST=0.0.0.0
PORT=8000
DEBUG=False
DEFAULT_MODEL=gpt-4o-mini
```

### Running the Application

1.  **Ensure your backend virtual environment is active** (if you created one).
2.  **Start the backend server:** From the project's root directory, run:
    ```bash
    cd backend
    python main.py
    ```
3.  **Access the application:** Open your web browser and navigate to:
    `http://localhost:8000` (or whatever port you configured in your .env file)

### Development Setup

If you want to run both the frontend and backend in development mode:

1. **Start the backend server:**
   ```bash
   cd backend
   python main.py
   ```
   This will run on port 8000 by default (or the port specified in your .env file)

2. **In a separate terminal, start the frontend development server:**
   ```bash
   cd frontend
   npm run dev
   ```
   This will run the Vite development server on port 5173

3. **Access the development version:**
   Open your browser and navigate to `http://localhost:5173`

### Troubleshooting

* **WebSocket Connection Issues:**
  * Ensure both the frontend and backend servers are running
  * Check that the WebSocket proxy in `frontend/vite.config.js` points to the correct backend port
  * If you change the backend port in `.env`, you must also update the WebSocket proxy in `vite.config.js`

* **Port Already in Use:**
  * If you get an error like "address already in use", try changing the port in your `.env` file
  * Remember to update the WebSocket proxy in `vite.config.js` to match the new port

* **Missing Dependencies:**
  * If you encounter missing dependencies, try installing from both requirements files:
    ```bash
    pip install -r backend/requirements.txt
    pip install -r requirements.txt
    ```

## Backend Architecture

NeonChat uses a modular architecture designed for maintainability, scalability, and clarity:

* **App Structure:**
  ```
  backend/
  └── app/
      ├── api/
      │   ├── routes/
      │   └── ws/
      ├── services/
      ├── models/
      └── utils/
  ```

* **Modules:**
  * **API Layer** (`api/`): Handles HTTP routes and WebSocket connections
    * `routes/`: HTTP endpoint definitions
    * `ws/`: WebSocket message handlers for different message types
  * **Service Layer** (`services/`): Contains business logic
    * `message_service.py`: Manages chat messages and history
    * `voice_service.py`: Handles speech-to-text and text-to-speech
    * `image_service.py`: Manages image generation
    * `api_service.py`: Centralizes API calls to AI providers
  * **Model Layer** (`models/`): Defines data structures
    * `message.py`: Message and chat history structures
    * `session.py`: User session management
  * **Utilities** (`utils/`): Helper functions
    * `config_utils.py`: Configuration and API key management
    * `file_utils.py`: File processing utilities
    * `audio_utils.py`: Audio format handling

* **Benefits:**
  * Clear separation of concerns
  * Improved maintainability
  * Easier to extend with new features
  * Better testability
  * Simplified onboarding for new developers

## Security Notes

* API keys stored in the `.env` file are excluded from version control via `.gitignore` to prevent accidental exposure.
* An example configuration file (`.env.example`) is provided with placeholder values to guide setup without exposing real credentials.
* The application uses the `python-dotenv` library to securely load environment variables from the `.env` file.
* When using the Settings UI, API keys are stored in the browser's local storage and are only sent to the backend when needed for API calls.

## Development

### Adding New API Providers

To add support for a new API provider:

1. Update the `config_utils.py` file to include the new provider's API key.
2. Create a new function in `api_calls.py` to handle the API calls to the new provider.
3. Update the frontend to include the new provider in the model selection dropdown.

### Conversation Debugging Features

The conversation debugging branch adds several new features to enhance the chat experience:

* **Audio Transcription**: Convert spoken audio to text using OpenAI's transcription API.
* **Real-time Voice Chat**: Engage in voice conversations with AI models using OpenAI's Realtime API.
* **Conversation Analysis**: Debug and analyze conversations for improved interaction quality.
* **Audio Playback**: Listen to AI-generated responses with text-to-speech capabilities.

These features require the following dependencies:
* FFmpeg for audio processing (included in the repository)
* pydub for audio format conversion
* OpenAI's Realtime API support

### Project Structure

* `backend/` - Contains all backend code
  * `main.py` - FastAPI application entry point
  * `api_calls.py` - Functions for making API calls to various providers
  * `config_utils.py` - Configuration management utilities
  * `realtime_api.py` - Handles real-time voice conversation features
  * `file_utils.py` - Utilities for file processing
  * `.env` - Environment variables (not in version control)
  * `.env.example` - Example environment variables file
* `frontend/` - Contains all frontend code
  * `static/` - Static files (HTML, CSS, JS)
  * `src/` - Source files for the frontend
  * `dist/` - Built frontend files (generated)
