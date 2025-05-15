// abacus-integration.js
// Integration with Abacus.ai features for NeonChat

// State management for Abacus.ai features
const abacusState = {
    // Image generation state
    imageGeneration: {
        prompt: '',
        size: '1024x1024',
        count: 1,
        quality: 'standard',
        loading: false,
        images: [],
        error: null
    },
    
    // Search state
    search: {
        query: '',
        type: 'normal',
        active: false,
        results: [],
        loading: false,
        error: null
    },
    
    // Diary entry state
    diary: {
        entryText: '',
        saving: false,
        saved: false,
        error: null
    },
    
    // Model selection state
    modelSelection: {
        currentModel: 'default', // 'default' for ChatGPT, 'abacus' for Abacus.ai
        availableModels: ['default'],
        selectedAbacusModel: null
    },
    
    // Conversation history for context management
    conversationHistory: []
};

// Function to initialize the Abacus.ai integration UI
function initAbacusIntegration() {
    console.log("Initializing Abacus.ai integration...");
    
    // Create the UI components
    createSidebar();
    createImageGenerationUI();
    createSearchUI();
    createDiaryUI();
    createModelSelectionUI();
    
    // Add event listeners
    addEventListeners();
    
    console.log("Abacus.ai integration initialized");
}

// Create a sidebar for all Abacus.ai features
function createSidebar() {
    // Create sidebar container if it doesn't exist
    let sidebar = document.getElementById('abacus-sidebar');
    if (sidebar) return; // Already exists
    
    sidebar = document.createElement('div');
    sidebar.id = 'abacus-sidebar';
    sidebar.className = 'abacus-sidebar collapsed';
    
    // Add a toggle button
    const toggleBtn = document.createElement('button');
    toggleBtn.id = 'abacus-sidebar-toggle';
    toggleBtn.className = 'abacus-sidebar-toggle';
    toggleBtn.innerHTML = '<span>◀</span>';
    toggleBtn.title = 'Toggle Abacus.ai Tools';
    
    // Add sections for each feature
    const imageSection = document.createElement('div');
    imageSection.id = 'abacus-image-section';
    imageSection.className = 'abacus-section';
    imageSection.innerHTML = '<h3>Image Generation</h3><div class="abacus-section-content" id="abacus-image-content"></div>';
    
    const searchSection = document.createElement('div');
    searchSection.id = 'abacus-search-section';
    searchSection.className = 'abacus-section';
    searchSection.innerHTML = '<h3>Search</h3><div class="abacus-section-content" id="abacus-search-content"></div>';
    
    const diarySection = document.createElement('div');
    diarySection.id = 'abacus-diary-section';
    diarySection.className = 'abacus-section';
    diarySection.innerHTML = '<h3>Diary Entry</h3><div class="abacus-section-content" id="abacus-diary-content"></div>';
    
    const modelSection = document.createElement('div');
    modelSection.id = 'abacus-model-section';
    modelSection.className = 'abacus-section';
    modelSection.innerHTML = '<h3>Model Selection</h3><div class="abacus-section-content" id="abacus-model-content"></div>';
    
    // Append all sections to the sidebar
    sidebar.appendChild(toggleBtn);
    sidebar.appendChild(imageSection);
    sidebar.appendChild(searchSection);
    sidebar.appendChild(diarySection);
    sidebar.appendChild(modelSection);
    
    // Append sidebar to the body
    document.body.appendChild(sidebar);
    
    // Add toggle event listener
    toggleBtn.addEventListener('click', toggleSidebar);
}

function toggleSidebar() {
    const sidebar = document.getElementById('abacus-sidebar');
    if (sidebar) {
        sidebar.classList.toggle('collapsed');
        
        // Update toggle button text
        const toggleBtn = document.getElementById('abacus-sidebar-toggle');
        if (toggleBtn) {
            toggleBtn.innerHTML = sidebar.classList.contains('collapsed') ? '<span>◀</span>' : '<span>▶</span>';
        }
    }
}

// Create UI for image generation
function createImageGenerationUI() {
    const container = document.getElementById('abacus-image-content');
    if (!container) return;
    
    container.innerHTML = `
        <form id="image-generation-form" class="abacus-form">
            <div class="form-group">
                <label for="img-prompt">Prompt</label>
                <textarea id="img-prompt" rows="3" class="form-control" placeholder="Describe the image you want to generate..." required></textarea>
            </div>
            <div class="form-group">
                <label for="img-size">Size</label>
                <select id="img-size" class="form-control">
                    <option value="512x512">Small (512x512)</option>
                    <option value="1024x1024" selected>Medium (1024x1024)</option>
                    <option value="1024x1792">Medium Tall (1024x1792)</option>
                </select>
            </div>
            <div class="form-group">
                <label for="img-count">Number of Images</label>
                <input type="number" id="img-count" min="1" max="4" value="1" class="form-control">
            </div>
            <div class="form-group">
                <label>Quality</label>
                <div class="radio-group">
                    <label>
                        <input type="radio" name="quality" value="cheaper" class="form-radio">
                        <span>Cheaper/Faster</span>
                    </label>
                    <label>
                        <input type="radio" name="quality" value="standard" checked class="form-radio">
                        <span>Standard</span>
                    </label>
                    <label>
                        <input type="radio" name="quality" value="expensive" class="form-radio">
                        <span>Expensive/Best</span>
                    </label>
                </div>
            </div>
            <button type="submit" id="generate-image-btn" class="abacus-btn">Generate Images</button>
        </form>
        <div id="image-generation-results" class="abacus-results">
            <!-- Generated images will be displayed here -->
        </div>
        <div id="image-generation-error" class="abacus-error"></div>
    `;
}

// Create UI for search features
function createSearchUI() {
    const container = document.getElementById('abacus-search-content');
    if (!container) return;
    
    container.innerHTML = `
        <div class="form-group">
            <label for="search-toggle">Enable Search Mode</label>
            <div class="toggle-switch">
                <input type="checkbox" id="search-toggle" class="toggle-input">
                <label for="search-toggle" class="toggle-label"></label>
            </div>
        </div>
        <div id="search-options" class="search-options hidden">
            <div class="form-group">
                <label for="search-type">Search Type</label>
                <div class="radio-group">
                    <label>
                        <input type="radio" name="search-type" value="normal" checked class="form-radio">
                        <span>Normal Search</span>
                    </label>
                    <label>
                        <input type="radio" name="search-type" value="deep_research" class="form-radio">
                        <span>Deep Research</span>
                    </label>
                </div>
            </div>
            <p class="search-info">
                When search is enabled, your chat input will be processed as a search query
            </p>
        </div>
    `;
}

// Create UI for diary entry
function createDiaryUI() {
    const container = document.getElementById('abacus-diary-content');
    if (!container) return;
    
    container.innerHTML = `
        <div class="form-group">
            <button id="save-diary-btn" class="abacus-btn">Save Chat as Diary Entry</button>
            <p class="diary-info">
                Saves the current conversation as a diary entry
            </p>
        </div>
        <div id="diary-saved-msg" class="abacus-success hidden">
            Diary entry saved successfully!
        </div>
        <div id="diary-error" class="abacus-error"></div>
    `;
}

// Create UI for model selection
function createModelSelectionUI() {
    const container = document.getElementById('abacus-model-content');
    if (!container) return;
    
    container.innerHTML = `
        <div class="form-group">
            <label for="model-select">Select Chat Model</label>
            <select id="model-select" class="form-control">
                <option value="default" selected>Default ChatGPT API</option>
                <option value="abacus-auto">Abacus.ai - Auto Model Picker</option>
                <!-- More Abacus.ai models will be added dynamically -->
            </select>
        </div>
        <div id="model-info" class="model-info">
            Using the default OpenAI ChatGPT API
        </div>
    `;
}

// Add event listeners for all UI components
function addEventListeners() {
    // Image generation form submission
    const imageForm = document.getElementById('image-generation-form');
    if (imageForm) {
        imageForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await generateImages();
        });
    }
    
    // Search toggle
    const searchToggle = document.getElementById('search-toggle');
    if (searchToggle) {
        searchToggle.addEventListener('change', (e) => {
            toggleSearchMode(e.target.checked);
        });
    }
    
    // Diary save button
    const diaryBtn = document.getElementById('save-diary-btn');
    if (diaryBtn) {
        diaryBtn.addEventListener('click', async () => {
            await saveDiaryEntry();
        });
    }
    
    // Model selection
    const modelSelect = document.getElementById('model-select');
    if (modelSelect) {
        modelSelect.addEventListener('change', (e) => {
            changeModel(e.target.value);
        });
    }
}

// Image generation function
async function generateImages() {
    const promptElem = document.getElementById('img-prompt');
    const sizeElem = document.getElementById('img-size');
    const countElem = document.getElementById('img-count');
    const qualityElems = document.getElementsByName('quality');
    const resultsElem = document.getElementById('image-generation-results');
    const errorElem = document.getElementById('image-generation-error');
    const generateBtn = document.getElementById('generate-image-btn');
    
    // Get values
    const prompt = promptElem.value.trim();
    if (!prompt) {
        errorElem.textContent = "Please enter a prompt";
        errorElem.classList.remove('hidden');
        return;
    }
    
    const size = sizeElem.value;
    const count = parseInt(countElem.value);
    let quality = 'standard';
    for (const radio of qualityElems) {
        if (radio.checked) {
            quality = radio.value;
            break;
        }
    }
    
    // Update state
    abacusState.imageGeneration = {
        ...abacusState.imageGeneration,
        prompt,
        size,
        count,
        quality,
        loading: true,
        error: null
    };
    
    // Update UI
    errorElem.textContent = '';
    errorElem.classList.add('hidden');
    resultsElem.innerHTML = '<div class="loading">Generating images...</div>';
    generateBtn.disabled = true;
    
    try {
        // Call the API
        const response = await fetch('/api/generate-image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt,
                size,
                count,
                quality
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update state
            abacusState.imageGeneration.images = data.images || [];
            abacusState.imageGeneration.loading = false;
            
            // Display images
            resultsElem.innerHTML = '';
            if (data.images && data.images.length > 0) {
                const grid = document.createElement('div');
                grid.className = 'image-grid';
                
                data.images.forEach((src, index) => {
                    const imgWrapper = document.createElement('div');
                    imgWrapper.className = 'image-wrapper';
                    
                    const img = document.createElement('img');
                    img.src = src;
                    img.alt = `Generated image ${index + 1}`;
                    img.loading = 'lazy';
                    
                    const sendBtn = document.createElement('button');
                    sendBtn.className = 'send-to-chat-btn';
                    sendBtn.textContent = 'Send to Chat';
                    sendBtn.addEventListener('click', () => sendImageToChat(src));
                    
                    imgWrapper.appendChild(img);
                    imgWrapper.appendChild(sendBtn);
                    grid.appendChild(imgWrapper);
                });
                
                resultsElem.appendChild(grid);
            } else {
                resultsElem.innerHTML = '<p>No images were generated. Please try again.</p>';
            }
        } else {
            throw new Error(data.error || 'Failed to generate images');
        }
    } catch (error) {
        console.error('Error generating images:', error);
        
        // Update state
        abacusState.imageGeneration.error = error.message;
        abacusState.imageGeneration.loading = false;
        
        // Update UI
        errorElem.textContent = `Error: ${error.message}`;
        errorElem.classList.remove('hidden');
        resultsElem.innerHTML = '';
    } finally {
        generateBtn.disabled = false;
    }
}

// Function to send a generated image to the chat
function sendImageToChat(imageUrl) {
    // Create an image message element
    const messageElement = document.createElement('div');
    messageElement.className = 'message message-user';
    
    const imgElement = document.createElement('img');
    imgElement.src = imageUrl;
    imgElement.alt = 'Generated image';
    imgElement.className = 'message-image';
    
    messageElement.appendChild(imgElement);
    
    // Add to chat messages
    const chatMessages = document.getElementById('chat-messages');
    if (chatMessages) {
        chatMessages.appendChild(messageElement);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Add to conversation history
    abacusState.conversationHistory.push({
        role: 'user',
        type: 'image',
        content: imageUrl
    });
}

// Toggle search mode
function toggleSearchMode(enabled) {
    const searchOptions = document.getElementById('search-options');
    
    // Update state
    abacusState.search.active = enabled;
    
    // Update UI
    if (searchOptions) {
        if (enabled) {
            searchOptions.classList.remove('hidden');
        } else {
            searchOptions.classList.add('hidden');
        }
    }
    
    // Update chat input placeholder
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.placeholder = enabled ? 'Enter your search query...' : 'Type your message...';
    }
}

// Save diary entry
async function saveDiaryEntry() {
    const errorElem = document.getElementById('diary-error');
    const savedMsg = document.getElementById('diary-saved-msg');
    const saveBtn = document.getElementById('save-diary-btn');
    
    // Get the last few messages from the chat
    const chatMessages = document.querySelectorAll('#chat-messages .message');
    if (!chatMessages || chatMessages.length === 0) {
        errorElem.textContent = "No chat messages to save";
        errorElem.classList.remove('hidden');
        return;
    }
    
    // Extract the last few messages (up to 5) as the entry text
    const lastMessages = Array.from(chatMessages).slice(-5);
    const entryText = lastMessages.map(msg => {
        const isAi = msg.classList.contains('message-ai');
        const content = msg.textContent.trim();
        return `${isAi ? 'AI: ' : 'User: '}${content}`;
    }).join('\n');
    
    // Update state
    abacusState.diary = {
        ...abacusState.diary,
        entryText,
        saving: true,
        saved: false,
        error: null
    };
    
    // Update UI
    errorElem.textContent = '';
    errorElem.classList.add('hidden');
    savedMsg.classList.add('hidden');
    saveBtn.disabled = true;
    
    try {
        // Call the API
        const response = await fetch('/api/save-diary', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                entry_text: entryText,
                user_id: window.clientId || 'anonymous',
                context: abacusState.conversationHistory.slice(-10) // Last 10 messages as context
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update state
            abacusState.diary.saving = false;
            abacusState.diary.saved = true;
            
            // Update UI
            savedMsg.classList.remove('hidden');
            
            // Hide success message after 3 seconds
            setTimeout(() => {
                savedMsg.classList.add('hidden');
            }, 3000);
        } else {
            throw new Error(data.error || 'Failed to save diary entry');
        }
    } catch (error) {
        console.error('Error saving diary entry:', error);
        
        // Update state
        abacusState.diary.error = error.message;
        abacusState.diary.saving = false;
        
        // Update UI
        errorElem.textContent = `Error: ${error.message}`;
        errorElem.classList.remove('hidden');
    } finally {
        saveBtn.disabled = false;
    }
}

// Change the chat model
function changeModel(modelId) {
    const modelInfo = document.getElementById('model-info');
    
    // Update state
    abacusState.modelSelection.currentModel = modelId.startsWith('abacus') ? 'abacus' : 'default';
    abacusState.modelSelection.selectedAbacusModel = modelId.startsWith('abacus') ? modelId : null;
    
    // Update UI
    if (modelInfo) {
        if (modelId === 'default') {
            modelInfo.textContent = 'Using the default OpenAI ChatGPT API';
        } else if (modelId === 'abacus-auto') {
            modelInfo.textContent = 'Using Abacus.ai with automatic model selection';
        } else {
            modelInfo.textContent = `Using Abacus.ai model: ${modelId.replace('abacus-', '')}`;
        }
    }
}

// Override the default chat submit function to handle Abacus.ai integration
async function handleChatSubmit(message) {
    // If search mode is active, use search endpoint
    if (abacusState.search.active) {
        const searchTypeElems = document.getElementsByName('search-type');
        let searchType = 'normal';
        for (const radio of searchTypeElems) {
            if (radio.checked) {
                searchType = radio.value;
                break;
            }
        }
        
        // Call search API and handle results
        return await performSearch(message, searchType);
    }
    
    // If using Abacus.ai model, use the chat-abacus endpoint
    if (abacusState.modelSelection.currentModel === 'abacus') {
        return await chatWithAbacus(message);
    }
    
    // Otherwise, use the default chat handling
    return null; // This signals to use the default chat handler
}

// Perform search using Abacus.ai
async function performSearch(query, type) {
    // Update state
    abacusState.search = {
        ...abacusState.search,
        query,
        type,
        loading: true,
        error: null
    };
    
    try {
        // Call the API
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query,
                type
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update state
            abacusState.search.results = data.results || [];
            abacusState.search.loading = false;
            
            // Format search results for display
            const formattedResults = formatSearchResults(data.results);
            
            // Return formatted results to be displayed in the chat
            return {
                content: formattedResults,
                type: 'search_results'
            };
        } else {
            throw new Error(data.error || 'Failed to perform search');
        }
    } catch (error) {
        console.error('Error performing search:', error);
        
        // Update state
        abacusState.search.error = error.message;
        abacusState.search.loading = false;
        
        // Return error message
        return {
            content: `Error performing search: ${error.message}`,
            type: 'error'
        };
    }
}

// Format search results for display in chat
function formatSearchResults(results) {
    if (!results || results.length === 0) {
        return "No search results found.";
    }
    
    let formattedText = "## Search Results\n\n";
    
    results.forEach((result, index) => {
        formattedText += `### ${index + 1}. ${result.title || 'Result'}\n`;
        if (result.url) {
            formattedText += `[${result.url}](${result.url})\n\n`;
        }
        if (result.snippet) {
            formattedText += `${result.snippet}\n\n`;
        }
    });
    
    return formattedText;
}

// Chat with Abacus.ai
async function chatWithAbacus(message) {
    try {
        // Call the API
        const response = await fetch('/api/chat-abacus', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt: message,
                model_id: abacusState.modelSelection.selectedAbacusModel === 'abacus-auto' ? null : abacusState.modelSelection.selectedAbacusModel,
                conversation_history: abacusState.conversationHistory.slice(-10) // Last 10 messages as context
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update conversation history
            abacusState.conversationHistory.push({
                role: 'user',
                content: message
            });
            
            abacusState.conversationHistory.push({
                role: 'assistant',
                content: data.response
            });
            
            // Return response to be displayed in the chat
            return {
                content: data.response,
                type: 'text'
            };
        } else {
            throw new Error(data.error || 'Failed to get response from Abacus.ai');
        }
    } catch (error) {
        console.error('Error chatting with Abacus.ai:', error);
        
        // Return error message
        return {
            content: `Error: ${error.message}`,
            type: 'error'
        };
    }
}

// Initialize when the page loads
document.addEventListener('DOMContentLoaded', () => {
    initAbacusIntegration();
    
    // Override the default chat submission if needed
    if (window.originalSubmitChat) {
        const originalSubmitChat = window.submitChat;
        window.submitChat = async function(message) {
            const result = await handleChatSubmit(message);
            if (result) {
                // Handle custom result formatting
                if (result.type === 'search_results' || result.type === 'text') {
                    // Add user message to chat
                    addMessageToChat(message, 'user');
                    
                    // Add AI response to chat
                    addMessageToChat(result.content, 'ai');
                    
                    return true; // Indicate that we've handled the submission
                } else if (result.type === 'error') {
                    // Display error message
                    addMessageToChat(result.content, 'error');
                    return true;
                }
            }
            
            // If we didn't handle it, use the original function
            return originalSubmitChat(message);
        };
    }
});

// Helper function to add a message to the chat
function addMessageToChat(content, role) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;
    
    const messageElement = document.createElement('div');
    messageElement.className = `message message-${role}`;
    
    if (role === 'error') {
        messageElement.className = 'message message-error';
    }
    
    if (content.startsWith('#') || content.includes('\n')) {
        // Treat as markdown if it has headings or line breaks
        messageElement.innerHTML = marked.parse(content);
    } else {
        messageElement.textContent = content;
    }
    
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
