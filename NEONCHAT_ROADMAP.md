NeonChat: Abacus.ai Integration & Feature Enhancement Roadmap
Project Goal: Refactor NeonChat to remove voice functionalities and integrate deeply with Abacus.ai for core AI tasks, including image generation, search, diary entries, and flexible model selection. Enhance UI/UX for these new features and maintain existing ChatGPT API interaction.
Key Technologies:
• Frontend: React, Tailwind CSS, HTML
• Backend: Python (e.g., Flask or FastAPI)
• AI Platform: Abacus.ai (for custom agents and models)
Phase 0: Project Setup & Abacus.ai SDK Familiarisation
Objective: Prepare the development environment and gain a thorough understanding of Abacus.ai's capabilities, particularly its Python SDK and agent interaction patterns.
• Task 0.1: Environment Setup & API Keys
o Ensure your Python backend and React frontend environments are up to date.
o Sign up for Abacus.ai if you haven't already.
o Obtain Abacus.ai API keys and store them securely (e.g., in .env files).
• Backend: ABACUS_API_KEY
• (Note: Frontend should not directly access these keys; all Abacus.ai calls go through your backend).
• Task 0.2: Abacus.ai Python SDK Deep Dive
o Action: Instruct the AI assistant to thoroughly review the Abacus.ai Python SDK documentation.
• Focus on:
• ApiClient initialisation and authentication.
• Creating, deploying, and managing "AI Agents" (especially CHAT and DEFAULT types).
• The structure of agent_function and how to pass data (e.g., prompts, parameters, context) to it.
• How agents return data.
• Available classes like AgentChatMessage, AgentConversation, AgentDataDocumentInfo for potential context management or data handling.
• Error handling.
o Example (Conceptual - for AI to research and adapt):
o # Conceptual Python snippet for AI to research
o # from abacusai import ApiClient, ApiException
o #
o # try:
o #     client = ApiClient(api_key="YOUR_ABACUS_API_KEY")
o #     # Example: List available agents or a specific agent
o #     # agents = client.list_agents(project_id="YOUR_PROJECT_ID")
o #     # print(agents)
o #
o #     # Example: Execute a deployed agent
o #     # response = client.execute_agent(
o #     #     deployment_token="AGENT_DEPLOYMENT_TOKEN", # or deployment_id
o #     #     deployment_id="AGENT_DEPLOYMENT_ID",
o #     #     keyword_arguments={'prompt': 'User query', 'user_id': '123'}
o #     # )
o #     # print(response.get('output_data_or_text'))
o # except ApiException as e:
o #     print(f"Abacus.ai API Error: {e}")

• Task 0.3: Define Abacus.ai Agent Strategy (High-Level)
o You will create agents in Abacus.ai for:
1. Image Generation Agent: Takes prompt, size, count, quality parameters.
2. Search Agent: Takes query, search type (normal/deep).
3. Diary Agent: Takes diary text, user ID; handles saving to Abacus.ai DB.
4. Model Picker Agent (Optional/Advanced): Takes user query, potentially suggests an LLM.
5. Generic LLM Agent: Takes prompt and a specified model ID to use for chat.
o This task is about planning what these agents will do. The actual creation in Abacus.ai is your responsibility, but the app's backend will need to know how to call them.
Phase 1: Core Cleanup - Voice Feature Removal
Objective: Systematically remove all code related to voice interaction from both frontend and backend to simplify the codebase.
• Task 1.1: Frontend Voice Feature Removal (React)
o Identify and remove all React components related to voice recording, playback, and voice UI controls (e.g., microphone buttons, voice activity indicators).
o Remove any voice-specific state management (e.g., in Context API, Redux, Zustand).
o Remove event handlers and utility functions associated with voice input/output.
o Clean up CSS/Tailwind classes related to removed voice UI elements.
• Task 1.2: Backend Voice Feature Removal (Python)
o Identify and remove API endpoints designed for voice data submission or processing.
o Remove any libraries or dependencies used exclusively for voice (e.g., speech-to-text, text-to-speech libraries, audio processing tools).
o Remove backend logic for handling audio streams, transcription, or voice synthesis.
• Task 1.3: Configuration and Documentation Update
o Remove any environment variables or configuration settings related to voice services.
o Update internal documentation or comments to reflect the removal of voice features.
Phase 2: Backend - Abacus.ai Integration Layer (Python)
Objective: Create robust backend API endpoints that will act as a proxy between your chat application and the Abacus.ai agents.
• Task 2.1: Setup Abacus.ai API Client in Backend
o Initialise the ApiClient from abacusai library using your API key. This should be done in a way that it can be reused across different API endpoints (e.g., as a singleton or part of an application context).
• Task 2.2: Develop API Endpoint for Image Generation
o Endpoint: POST /api/generate-image
o Request Body: { "prompt": "string", "size": "string (e.g., '512x512', '1024x1024')", "count": "integer", "quality": "string (e.g., 'standard', 'hd' or 'cheaper', 'expensive')" }
o Logic:
• Receive request.
• Call the designated "Image Generation Agent" in Abacus.ai using the Python SDK, passing the parameters.
• Return the image URLs or relevant data from Abacus.ai.
o Example (Conceptual Python - Flask/FastAPI style):
o # from flask import Flask, request, jsonify
o # from abacusai import ApiClient, ApiException
o #
o # app = Flask(__name__)
o # abacus_client = ApiClient(api_key="YOUR_ABACUS_API_KEY")
o # IMAGE_AGENT_DEPLOYMENT_ID = "YOUR_IMAGE_AGENT_DEPLOYMENT_ID" # or token
o #
o # @app.route('/api/generate-image', methods=['POST'])
o # def generate_image():
o #     data = request.json
o #     try:
o #         response = abacus_client.execute_agent(
o #             deployment_id=IMAGE_AGENT_DEPLOYMENT_ID,
o #             keyword_arguments={
o #                 'prompt': data.get('prompt'),
o #                 'size': data.get('size'),
o #                 'num_images': data.get('count'),
o #                 'quality_mode': data.get('quality')
o #             }
o #         )
o #         # Assume agent returns a list of image URLs in 'result' key
o #         return jsonify({"success": True, "images": response.get('result', {}).get('image_urls', [])})
o #     except ApiException as e:
o #         return jsonify({"success": False, "error": str(e)}), 500
o #     except Exception as e:
o #         return jsonify({"success": False, "error": f"An unexpected error occurred: {str(e)}"}), 500

• Task 2.3: Develop API Endpoint for Search
o Endpoint: POST /api/search
o Request Body: { "query": "string", "type": "string ('normal' or 'deep_research')" }
o Logic: Call the "Search Agent" in Abacus.ai.
• Task 2.4: Develop API Endpoint for Diary Entries
o Endpoint: POST /api/save-diary
o Request Body: { "entry_text": "string", "user_id": "string" } (pass conversation history/context if needed, see Phase 4)
o Logic: Call the "Diary Agent" in Abacus.ai.
• Task 2.5: Develop API Endpoint for Generic Chat (via Abacus.ai Model)
o Endpoint: POST /api/chat-abacus
o Request Body: { "prompt": "string", "model_id": "string (Abacus.ai model/agent ID)", "conversation_history": "array (optional)" }
o Logic: Call the designated "Generic LLM Agent" or a specific model deployment in Abacus.ai.
• Task 2.6: Error Handling and Logging
o Implement comprehensive error handling for all Abacus.ai API calls.
o Log requests and responses for debugging.
Phase 3: Frontend - UI/UX for Abacus.ai Features (React & Tailwind CSS)
Objective: Design and implement intuitive UI controls for interacting with the new Abacus.ai-powered features. These controls should be neatly organised and not obstruct the main chat canvas.
• Task 3.1: Design UI Layout for New Controls
o Suggestion: Consider a dedicated sidebar, a toolbar above or below the chat input, or context-sensitive buttons. Avoid popups that cover the chat.
o Example Layout Idea: A collapsible right sidebar with sections for "Image Generation", "Search Tools", "Diary", and "Model Settings".
• Task 3.2: Implement Image Generation UI
o Input field for prompt.
o Dropdown/Radio buttons for image size (e.g., "Small (512x512)", "Medium (1024x1024)", "Large (2048x2048)").
o Input (number) for number of images.
o Dropdown/Radio buttons for quality ("Cheaper/Faster", "Expensive/Best Quality").
o "Generate" button.
o Display area for generated images (or links).
o Example React Component Snippet (Conceptual):
o // // ImageGeneratorForm.jsx (Conceptual)
o // import React, { useState } from 'react';
o //
o // const ImageGeneratorForm = () => {
o //   const [prompt, setPrompt] = useState('');
o //   const [size, setSize] = useState('1024x1024');
o //   const [count, setCount] = useState(1);
o //   const [quality, setQuality] = useState('standard');
o //   const [isLoading, setIsLoading] = useState(false);
o //   const [images, setImages] = useState([]);
o //   const [error, setError] = useState(null);
o //
o //   const handleSubmit = async (e) => {
o //     e.preventDefault();
o //     setIsLoading(true);
o //     setError(null);
o //     setImages([]);
o //     try {
o //       const response = await fetch('/api/generate-image', {
o //         method: 'POST',
o //         headers: { 'Content-Type': 'application/json' },
o //         body: JSON.stringify({ prompt, size, count, quality }),
o //       });
o //       const data = await response.json();
o //       if (data.success) {
o //         setImages(data.images);
o //       } else {
o //         setError(data.error || 'Failed to generate images.');
o //       }
o //     } catch (err) {
o //       setError('An error occurred: ' + err.message);
o //     } finally {
o //       setIsLoading(false);
o //     }
o //   };
o //
o //   return (
o //     <div className="p-4 bg-gray-800 rounded-lg shadow">
o //       <h3 className="text-lg font-semibold mb-3 text-white">Image Generation</h3>
o //       <form onSubmit={handleSubmit} className="space-y-3">
o //         {/* Prompt Input */}
o //         <div>
o //           <label htmlFor="img-prompt" className="block text-sm font-medium text-gray-300">Prompt</label>
o //           <textarea id="img-prompt" value={prompt} onChange={(e) => setPrompt(e.target.value)} rows="3" className="mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2" required />
o //         </div>
o //         {/* Size Selector */}
o //         <div>
o //           <label htmlFor="img-size" className="block text-sm font-medium text-gray-300">Size</label>
o //           <select id="img-size" value={size} onChange={(e) => setSize(e.target.value)} className="mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2">
o //             <option value="512x512">Small (512x512)</option>
o //             <option value="1024x1024">Medium (1024x1024)</option>
o //             <option value="1024x1792">Medium Tall (1024x1792)</option>
o //           </select>
o //         </div>
o //         {/* Count Input */}
o //         <div>
o //           <label htmlFor="img-count" className="block text-sm font-medium text-gray-300">Number of Images</label>
o //           <input type="number" id="img-count" value={count} onChange={(e) => setCount(parseInt(e.target.value))} min="1" max="4" className="mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2" />
o //         </div>
o //         {/* Quality Selector */}
o //         <div>
o //           <label className="block text-sm font-medium text-gray-300">Quality</label>
o //           <div className="mt-1 flex space-x-4">
o //             <label className="inline-flex items-center">
o //               <input type="radio" name="quality" value="cheaper" checked={quality === 'cheaper'} onChange={(e) => setQuality(e.target.value)} className="form-radio h-4 w-4 text-indigo-600 border-gray-500 bg-gray-700 focus:ring-indigo-500" />
o //               <span className="ml-2 text-gray-300">Cheaper/Faster</span>
o //             </label>
o //             <label className="inline-flex items-center">
o //               <input type="radio" name="quality" value="expensive" checked={quality === 'expensive'} onChange={(e) => setQuality(e.target.value)} className="form-radio h-4 w-4 text-indigo-600 border-gray-500 bg-gray-700 focus:ring-indigo-500" />
o //               <span className="ml-2 text-gray-300">Expensive/Best</span>
o //             </label>
o //           </div>
o //         </div>
o //         <button type="submit" disabled={isLoading} className="w-full inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-800 focus:ring-indigo-500 disabled:opacity-50">
o //           {isLoading ? 'Generating...' : 'Generate Images'}
o //         </button>
o //       </form>
o //       {error && <p className="mt-2 text-sm text-red-400">{error}</p>}
o //       {images.length > 0 && (
o //         <div className="mt-4 grid grid-cols-2 gap-2">
o //           {images.map((src, index) => <img key={index} src={src} alt={`Generated ${index + 1}`} className="rounded-md" />)}
o //         </div>
o //       )}
o //     </div>
o //   );
o // };
o // export default ImageGeneratorForm;

• Task 3.3: Implement Search UI
o Toggle button or switch for "Search" mode.
o Perhaps another toggle for "Deep Research" if "Search" is active.
o When active, user's chat input could be routed to the /api/search backend endpoint.
• Task 3.4: Implement Diary Entry UI
o A button "Save as Diary Entry".
o When clicked, it could take the current chat content (or a summary) and send it to /api/save-diary.
o Alternatively, a dedicated text area for diary entries.
• Task 3.5: Implement Model Selection UI (for Abacus.ai & existing ChatGPT)
o A dropdown menu to select the "Chat Engine" or "Model".
o Options could include:
• "Default ChatGPT API"
• "Abacus.ai - Auto Model Picker" (if you implement this agent)
• "Abacus.ai - Model X" (if you allow direct selection of Abacus.ai models/agents)
• "Abacus.ai - Model Y"
o The selection would determine which backend endpoint (/api/chat for default ChatGPT, or /api/chat-abacus for Abacus.ai) is called.
• Task 3.6: Styling and Responsiveness
o Ensure all new UI elements are styled with Tailwind CSS, are visually appealing, and responsive.
Phase 4: Context Management Strategy
Objective: Implement a mechanism to maintain conversational context, especially when switching between or repeatedly calling Abacus.ai agents.
• Task 4.1: Research Abacus.ai Agent Context Capabilities
o Action: Instruct the AI assistant to investigate if Abacus.ai agents (via agent_function or SDK features like AgentConversation) have built-in mechanisms for managing conversation history or session state.
o If Abacus.ai offers native context management for agents, prioritise using that.
• Task 4.2: Client-Side Context Management (If Abacus.ai doesn't handle it fully)
o Maintain the conversation history (array of messages with user and assistant roles) in the React app's state.
o When calling an Abacus.ai agent (via your backend), decide how much context to send:
• Option A: Send the last N messages.
• Option B: Send a summarized version of the conversation.
• Option C: Allow the Abacus.ai agent's agent_function to specify what context it needs.
• Task 4.3: Backend - Passing Context to Abacus.ai Agents
o Modify the backend API endpoints (from Phase 2) to accept an optional conversation_history or context parameter.
o Pass this context to the keyword_arguments when calling abacus_client.execute_agent(...).
o The Abacus.ai agent_function you design will need to be able to receive and use this context.
o Example (Conceptual Python - Diary Agent):
o # # In your Abacus.ai agent_function for the Diary Agent:
o # def agent_function(entry_text, user_id, conversation_history=None):
o #     # ... process entry_text ...
o #     # ... if conversation_history is provided, use it for additional context ...
o #     # ... save to Abacus.ai database ...
o #     # return {"status": "saved", "entry_id": "123"}
o #     pass

• Task 4.4: Context for Specific Features
o Diary: When "Save as Diary Entry" is clicked, the app could send the current message or the last few messages as context along with the explicit diary text.
o Follow-up questions to Search/Image Gen: If a user asks a follow-up question after a search result or image generation, the original query/prompt and the result could be part of the context sent to the relevant Abacus.ai agent or the general chat model.
Phase 5: Integrating Basic ChatGPT API & Abacus.ai Model Selection
Objective: Ensure the existing direct ChatGPT API functionality remains and integrate the model selection UI.
• Task 5.1: Verify Existing ChatGPT API Integration
o Ensure the current /api/chat (or similar) endpoint that calls the ChatGPT API directly is still functional.
• Task 5.2: Frontend Logic for Model Selection
o Based on the dropdown selection (from Task 3.5):
• If "Default ChatGPT API" is selected, the frontend sends chat messages to your existing ChatGPT backend endpoint.
• If an "Abacus.ai..." option is selected, the frontend sends chat messages to the /api/chat-abacus endpoint, including the chosen model_id (which could be an Abacus.ai agent ID or deployment ID).
• Task 5.3: Backend Logic for Abacus.ai Model Picker Agent (Optional)
o If you implement an "Auto Model Picker" agent in Abacus.ai:
• The /api/chat-abacus endpoint, when model_id is "auto_picker_agent_id", would first call this agent with the user's prompt.
• This agent would return the ID of the actual Abacus.ai model/agent to use.
• Your backend would then make a second call to that chosen model/agent with the original prompt.
Phase 6: New Feature Exploration & Implementation (Optional)
Objective: Consider and plan for additional useful features leveraging Abacus.ai.
• Task 6.1: Fact-Checker Functionality
o Idea: Create an "Fact Check Agent" in Abacus.ai.
o UI: A button "Fact Check this Statement" or a command /factcheck [statement].
o Backend: An endpoint /api/fact-check that calls this Abacus.ai agent.
o Abacus.ai Agent Logic: The agent would take the statement, use search capabilities (internal or external via tools), and return a summary with sources or a confidence score.
• Task 6.2: Other Potential Features
o Summarisation Agent
o Translation Agent
o Code Generation/Explanation Agent (if Abacus.ai supports this well)
o Workflow Automation: Trigger multi-step processes in Abacus.ai based on chat commands.
Phase 7: Testing, Documentation, and Deployment
Objective: Ensure the application is robust, well-documented, and ready for deployment.
• Task 7.1: Comprehensive Testing
o Unit tests for backend API endpoints (Python).
o Unit and integration tests for React components.
o End-to-end testing of all features:
• Basic chat (ChatGPT API).
• Image generation (all options).
• Search (normal and deep).
• Diary entries.
• Model selection and chat via Abacus.ai.
• Context persistence across interactions.
• Error handling and user feedback.
• Task 7.2: Documentation
o Update README with new setup instructions (Abacus.ai API key).
o Document new API endpoints.
o User guide for new features.
o Internal documentation for the Abacus.ai agent interactions.
• Task 7.3: Build and Deployment
o Prepare frontend build (React).
o Configure backend for production (e.g., Gunicorn/Uvicorn for Python).
o Deploy to your hosting environment.
This roadmap provides a structured approach. Remember that the actual implementation of agents within Abacus.ai is a separate task that you will handle on their platform, but this plan focuses on how your chat application will interact with those agents. Good luck!

