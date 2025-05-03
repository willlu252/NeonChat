# NeonChat

## Description

NeonChat is a web-based chat application designed as a wrapper to interact with various Large Language Models (LLMs). Select your preferred model provider, configure your API key via the secure settings interface, and start chatting.

This project serves as a foundation for experimenting with different AI models and is intended to be expanded with more features over time.

## Features

* Chat interface supporting various AI models.
* Currently supported providers: OpenAI, Google AI, Anthropic, DeepSeek, Perplexity.
* Real-time interaction using WebSockets.
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
* Node.js and `npm` (or `yarn`)

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

4.  **Install frontend dependencies:**
    * *(Run these commands in the root directory)*
        ```bash
        cd frontend
        npm install 
        ```
        *(or `yarn install` if you use Yarn)*

5.  **Build the frontend:**
    * *(This command uses the build script defined in your `package.json`)*
        ```bash
        npm run build
        ```
        *(or `yarn build`)*
        This should generate the static files in the `frontend/dist` directory, which the FastAPI backend serves.

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
    `http://localhost:8000`

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

### Project Structure

* `backend/` - Contains all backend code
  * `main.py` - FastAPI application entry point
  * `api_calls.py` - Functions for making API calls to various providers
  * `config_utils.py` - Configuration management utilities
  * `.env` - Environment variables (not in version control)
  * `.env.example` - Example environment variables file
* `frontend/` - Contains all frontend code
  * `static/` - Static files (HTML, CSS, JS)
  * `src/` - Source files for the frontend
  * `dist/` - Built frontend files (generated)
