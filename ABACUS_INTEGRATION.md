# Abacus.ai Integration for NeonChat

## Overview

This document provides a comprehensive guide to the Abacus.ai integration in NeonChat. The integration provides enhanced AI capabilities including image generation, search functionality, diary entry management, and flexible model selection.

## Architecture

The integration follows a layered architecture:

```
Frontend (UI Components)
    ↓
Backend API (REST Endpoints)
    ↓
Backend Services (Abacus.ai SDK)
    ↓
Abacus.ai Platform
```

### Components

1. **Frontend**
   - UI Components for image generation, search, diary entries, and model selection
   - Sidebar toggle for accessing Abacus.ai features
   - JavaScript for handling API calls and responses

2. **Backend API**
   - RESTful endpoints for all Abacus.ai features
   - Request/response validation
   - Error handling

3. **Backend Services**
   - Abacus.ai SDK integration
   - Service methods for each Abacus.ai feature
   - Error handling and logging

## Features

### 1. Image Generation

Generate high-quality images from text prompts using Abacus.ai's image generation capabilities.

**Frontend:**
- Prompt input field
- Size selection
- Count selection
- Quality options
- Results display area

**API Endpoint:**
- `POST /api/generate-image`

**Request Body:**
```json
{
  "prompt": "A futuristic neon city skyline with flying cars",
  "size": "1024x1024",
  "count": 1,
  "quality": "standard"
}
```

**Response:**
```json
{
  "success": true,
  "images": ["https://abacus.ai/generated-images/image1.png"]
}
```

### 2. Search

Perform powerful web searches with optional deep research capabilities.

**Frontend:**
- Search toggle
- Search type selection (normal or deep research)
- Results display in chat

**API Endpoint:**
- `POST /api/search`

**Request Body:**
```json
{
  "query": "latest advancements in AI technology",
  "type": "normal"
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "title": "Recent AI Advancements",
      "content": "Summary of content...",
      "url": "https://example.com/ai-news"
    }
  ],
  "search_type": "normal"
}
```

### 3. Diary Entries

Save and manage diary entries from chat conversations.

**Frontend:**
- Save as diary entry button
- Diary confirmation message

**API Endpoint:**
- `POST /api/save-diary`

**Request Body:**
```json
{
  "entry_text": "Today I learned about Abacus.ai integration.",
  "user_id": "user123",
  "context": [
    {"role": "user", "content": "Previous messages for context"}
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Diary entry saved successfully",
  "entry_id": "entry_12345"
}
```

### 4. Model Selection

Flexible model selection for different types of queries and tasks.

**Frontend:**
- Model dropdown selector
- Model information display

**API Endpoint:**
- Uses the chat endpoint with model specification
- Model picker logic is handled on the backend

## Setup Instructions

### Prerequisites

- Node.js and npm for frontend
- Python 3.8+ for backend
- Abacus.ai account and API key

### Installation

1. **Backend Setup**
   
   Install the required dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   
   Create a `.env` file in the backend directory with your Abacus.ai credentials:
   ```
   ABACUS_API_KEY=your_api_key_here
   ABACUS_IMAGE_AGENT_ID=your_image_generation_agent_id
   ABACUS_SEARCH_AGENT_ID=your_search_agent_id
   ABACUS_DIARY_AGENT_ID=your_diary_agent_id
   ABACUS_MODEL_PICKER_AGENT_ID=your_model_picker_agent_id
   ABACUS_GENERIC_LLM_AGENT_ID=your_generic_llm_agent_id
   ```

3. **Frontend Setup**
   
   The frontend files are already set up. Make sure the backend server is running for the frontend to connect to the API endpoints.

### Testing

Run the integration test script to verify your setup:

```bash
cd backend
python tests/test_abacus_integration.py
```

This will test all Abacus.ai features and report any issues.

## Usage

1. Start the backend server:
   ```bash
   cd backend
   python main.py
   ```

2. Open the frontend application in your browser.

3. Use the sidebar toggle button to access Abacus.ai features.

4. Generate images, perform searches, save diary entries, and switch between models as needed.

## Troubleshooting

1. **API Key Issues**
   - Ensure your Abacus.ai API key is correctly set in the `.env` file
   - Check that your API key has the necessary permissions

2. **Missing Agent IDs**
   - Verify that all agent deployment IDs are correctly set in the `.env` file
   - Ensure the agents are deployed and active in your Abacus.ai account

3. **SDK Installation**
   - If you encounter import errors, make sure the Abacus.ai SDK is installed:
     ```bash
     pip install abacusai
     ```

4. **Frontend Connection Issues**
   - Check that the backend server is running on the expected port
   - Verify network connectivity between frontend and backend

## Roadmap

Future enhancements planned for the Abacus.ai integration:

1. Additional image generation models and options
2. Advanced search filters and customization
3. Diary entry categorization and search capabilities
4. More granular model selection based on task type
5. Analytics for Abacus.ai feature usage

## Security Considerations

- API keys are never exposed in the frontend code
- All Abacus.ai API calls are made through the backend
- User data is handled according to privacy best practices
- Sensitive operations require authentication
