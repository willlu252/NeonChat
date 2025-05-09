// Use a script tag for marked in the HTML instead of import
let marked;
if (window.marked) {
    marked = window.marked;
    console.log("app.js: Using globally loaded marked library");
} else {
    console.error("app.js: marked library not found! Make sure to include the script tag in HTML");
}

console.log("app.js: Script loaded");

// --- Global Helper Functions ---
let chatCanvas;
function formatMessageContent(content) { if (!content) return ''; try { return marked.parse(content || ''); } catch (e) { console.error("Markdown error:", e); return content; } }

// Convert base64 to blob for audio playback
function base64ToBlob(base64, mimeType) {
    const byteCharacters = atob(base64);
    const byteArrays = [];
    
    for (let offset = 0; offset < byteCharacters.length; offset += 512) {
        const slice = byteCharacters.slice(offset, offset + 512);
        
        const byteNumbers = new Array(slice.length);
        for (let i = 0; i < slice.length; i++) {
            byteNumbers[i] = slice.charCodeAt(i);
        }
        
        const byteArray = new Uint8Array(byteNumbers);
        byteArrays.push(byteArray);
    }
    
    return new Blob(byteArrays, { type: mimeType });
}

// Create WAV header for PCM16 audio
function createWavHeader(dataLength, numChannels, sampleRate, bitsPerSample) {
    const headerLength = 44;
    const wavHeader = new Uint8Array(headerLength);
    
    // RIFF chunk descriptor
    writeString(wavHeader, 0, 'RIFF');                      // ChunkID
    writeInt32(wavHeader, 4, 36 + dataLength);              // ChunkSize
    writeString(wavHeader, 8, 'WAVE');                      // Format
    
    // fmt sub-chunk
    writeString(wavHeader, 12, 'fmt ');                     // Subchunk1ID
    writeInt32(wavHeader, 16, 16);                          // Subchunk1Size (16 for PCM)
    writeInt16(wavHeader, 20, 1);                           // AudioFormat (1 for PCM)
    writeInt16(wavHeader, 22, numChannels);                 // NumChannels
    writeInt32(wavHeader, 24, sampleRate);                  // SampleRate
    writeInt32(wavHeader, 28, sampleRate * numChannels * bitsPerSample / 8); // ByteRate
    writeInt16(wavHeader, 32, numChannels * bitsPerSample / 8); // BlockAlign
    writeInt16(wavHeader, 34, bitsPerSample);               // BitsPerSample
    
    // data sub-chunk
    writeString(wavHeader, 36, 'data');                     // Subchunk2ID
    writeInt32(wavHeader, 40, dataLength);                  // Subchunk2Size
    
    return wavHeader;
}

// Helper functions for writing to the WAV header
function writeString(dataView, offset, string) {
    for (let i = 0; i < string.length; i++) {
        dataView[offset + i] = string.charCodeAt(i);
    }
}

function writeInt16(dataView, offset, value) {
    dataView[offset] = value & 0xff;
    dataView[offset + 1] = (value >> 8) & 0xff;
}

function writeInt32(dataView, offset, value) {
    dataView[offset] = value & 0xff;
    dataView[offset + 1] = (value >> 8) & 0xff;
    dataView[offset + 2] = (value >> 16) & 0xff;
    dataView[offset + 3] = (value >> 24) & 0xff;
}

window.displayMessage = (message, useTypewriter = false) => {
     const localChatMessages = document.getElementById('chat-messages');
     if (!localChatMessages || !message || !message.role) return;
     const messageElement = document.createElement('div');
     messageElement.className = `message ${message.role === 'user' ? 'message-user' : 'message-ai'}`;
     if (message.role === 'system') { messageElement.classList.add('message-system'); messageElement.classList.remove('message-ai'); }
     if (message.type === 'image' && message.content) {
         // Create image container
         const imgContainer = document.createElement('div');
         imgContainer.className = 'message-image-container';
         
         // Create and setup image element
         const img = document.createElement('img');
         img.src = message.content;
         img.alt = 'Shared image';
         img.className = 'message-image';
         img.onerror = () => {
             img.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgZmlsbC1ydWxlPSJldmVub2RkIiBjbGlwLXJ1bGU9ImV2ZW5vZGQiPjxwYXRoIGQ9Ik0yNCAxMmMwIDYuNjIzLTUuMzc3IDEyLTEyIDEycy0xMi01LjM3Ny0xMi0xMiA1LjM3Ny0xMiAxMi0xMiAxMiA1LjM3NyAxMiAxMnptLTEyIDFjLjU1NyAwIDEtLjQ0OCAxLTEgMC0uNTUyLS40NDMtMS0xLTFzLTEgLjQ0OC0xIDFjMCAuNTUyLjQ0MyAxIDEgMXptMS41NzUgNi43MjNjLS4xNDYtLjY2Ny0uODQtMi43MjMtMi41NzUtMi43MjMtMS43MjggMC0yLjQyOSAyLjA1LTIuNTc1IDIuNzIzLS4xMjcuNTc4LjIuODI3LjQ0LjgyN2g0LjI3Yy4yNCAwIC41NjctLjI0OS40NC0uODI3em0tLjU3NS0xMi43MjNjMCAuODI3LS42NzMgMS41LTEuNSAxLjVzLTEuNS0uNjczLTEuNS0xLjUuNjczLTEuNSAxLjUtMS41IDEuNS42NzMgMS41IDEuNXoiLz48L3N2Zz4=';
             img.alt = 'Image failed to load';
         };
         
         // Add image to container
         imgContainer.appendChild(img);
         
         // Add caption if available
         if (message.caption) {
             const caption = document.createElement('div');
             caption.className = 'message-image-caption';
             caption.textContent = message.caption;
             imgContainer.appendChild(caption);
         }
         
         // Add container to message
         messageElement.appendChild(imgContainer);
     }
     else if (useTypewriter && message.role === 'assistant') { messageElement.classList.add('typewriter'); typewriterEffect(messageElement, message.content || ''); }
     else { messageElement.innerHTML = formatMessageContent(message.content || ''); }
     localChatMessages.appendChild(messageElement);
     requestAnimationFrame(() => { if (chatCanvas) chatCanvas.scrollTop = chatCanvas.scrollHeight; }); // Use global chatCanvas
};
function typewriterEffect(element, text, speed = 5) {
    let i = 0;
    element.textContent = '';
    
    function type() {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
            setTimeout(type, speed);
            
            // Auto-scroll as typing happens
            if (chatCanvas) {
                chatCanvas.scrollTop = chatCanvas.scrollHeight;
            }
        } else {
            // When typing is complete, render with markdown
            element.innerHTML = formatMessageContent(text);
            element.classList.remove('typewriter');
            
            // Final scroll after markdown rendering
            if (chatCanvas) {
                chatCanvas.scrollTop = chatCanvas.scrollHeight;
            }
        }
    }
    
    type();
}
function autoResizeInput() { 
    if (!this || typeof this.scrollHeight === 'undefined') return; 
    this.style.height = 'auto'; 
    const newHeight = this.scrollHeight; 
    const minHeight = 40; 
    const maxHeight = 150; // Match the CSS max-height valnue
    
    // Set the height within min and max constraints
    this.style.height = Math.min(Math.max(minHeight, newHeight), maxHeight) + 'px';
    
    // Enable or disable scrolling based on content height
    this.style.overflowY = newHeight > maxHeight ? 'auto' : 'hidden';
}
window.showTypingIndicator = () => { const el = document.querySelector('.typing-indicator'); if (el) el.classList.remove('hidden'); /* + scroll */ };
window.hideTypingIndicator = () => { const el = document.querySelector('.typing-indicator'); if (el) el.classList.add('hidden'); };
// --- END Global Helper Functions ---

document.addEventListener('DOMContentLoaded', () => {
    console.log("app.js: DOMContentLoaded fired");

    // --- Setup UI Elements ---
    chatCanvas = document.querySelector('.chat-canvas-revert');
    const chatMessagesContainer = document.getElementById('chat-messages');
    const chatInput = document.querySelector('#chat-input');
    const sendButton = document.querySelector('#send-button');
    const fileInput = document.getElementById('file-input');
    const imagePreview = document.getElementById('image-preview');
    const previewImage = document.getElementById('preview-image');
    const clearImageButton = document.getElementById('clear-image');
    const clearHistoryButton = document.getElementById('clear-history-button');
    
    // Voice and image generation elements
    const voiceRecordBtn = document.getElementById('voice-record-btn');
    const generateImageBtn = document.getElementById('generate-image-btn');
    const imageGenModal = document.getElementById('image-gen-modal');
    const imagePromptInput = document.getElementById('image-prompt');
    const imageSizeSelect = document.getElementById('image-size');
    const imageQualitySelect = document.getElementById('image-quality');
    const imageStyleSelect = document.getElementById('image-style');
    const generateImageSubmitBtn = document.getElementById('generate-image-submit-btn');
    const cancelImageBtn = document.getElementById('cancel-image-btn');
    const recordingIndicator = document.getElementById('recording-indicator');
    const recordingTimeDisplay = document.getElementById('recording-time');
    const stopRecordingBtn = document.getElementById('stop-recording-btn');
    
    // Settings elements
    const voiceEnabledSetting = document.getElementById('voice-enabled-setting');
    const voiceTypeSetting = document.getElementById('voice-type-setting');
    const voiceSpeedSetting = document.getElementById('voice-speed-setting');
    const voiceSpeedValue = document.getElementById('voice-speed-value');
    const imageSizeSetting = document.getElementById('image-size-setting');
    const imageQualitySetting = document.getElementById('image-quality-setting');
    const imageStyleSetting = document.getElementById('image-style-setting');
    
    // Voice recording variables
    let mediaRecorder = null;
    let audioChunks = [];
    let recordingTimer = null;
    let recordingSeconds = 0;
    
    // Voice and image settings
    let voiceEnabled = localStorage.getItem('voice_enabled') === 'true';
    let conversationalMode = localStorage.getItem('conversational_mode') === 'true';
    let conversationMode = localStorage.getItem('conversation_mode') || 'cheap';
    let selectedVoice = localStorage.getItem('selected_voice') || 'alloy';
    let voiceSpeed = parseFloat(localStorage.getItem('voice_speed') || '1.0');
    let defaultImageSize = localStorage.getItem('image_size') || '1024x1024';
    let defaultImageQuality = localStorage.getItem('image_quality') || 'standard';
    let defaultImageStyle = localStorage.getItem('image_style') || 'vivid';
    
    // Navigation elements
    const chatNav = document.getElementById('chat-nav');
    const settingsNav = document.getElementById('settings-nav');
    const projectsNav = document.getElementById('projects-nav');
    const modelsNav = document.getElementById('models-nav');
    
    // View elements
    const chatView = document.getElementById('chat-view');
    const settingsView = document.getElementById('settings-view');
    const projectsView = document.getElementById('projects-view');
    const modelsView = document.getElementById('models-view');
    
    // Sidebar toggle
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('main');
    
    // Project elements
    const createProjectBtn = document.getElementById('create-project-btn');
    const projectModal = document.getElementById('project-modal');
    const projectsList = document.getElementById('projects-list');
    const projectName = document.getElementById('project-name');
    const projectDescription = document.getElementById('project-description');
    const projectRules = document.getElementById('project-rules');
    const saveProjectBtn = document.getElementById('save-project-btn');
    const cancelProjectBtn = document.getElementById('cancel-project-btn');
    
    // Current selected image (if any)
    let currentImage = null;
    let editingProjectIndex = null;
    let projects = [];
    
    // Function to handle pasted image data
    function handlePastedImage(pasteEvent) {
        const items = (pasteEvent.clipboardData || pasteEvent.originalEvent.clipboardData).items;
        
        for (const item of items) {
            if (item.type.indexOf('image') === 0) {
                // We found an image in the clipboard
                const blob = item.getAsFile();
                currentImage = blob;
                
                // Create a preview of the pasted image
                const reader = new FileReader();
                reader.onload = (event) => {
                    previewImage.src = event.target.result;
                    imagePreview.classList.remove('hidden');
                };
                reader.readAsDataURL(blob);
                
                // Prevent the default paste behavior
                pasteEvent.preventDefault();
                break;
            }
        }
    }
    
    // Load projects from localStorage
    try {
        const savedProjects = localStorage.getItem('tron_projects');
        if (savedProjects) {
            projects = JSON.parse(savedProjects);
            renderProjects();
        }
    } catch (e) {
        console.error("app.js: Error loading projects:", e);
    }
    
    // Navigation handling
    function setActiveView(view) {
        // Hide all views
        chatView.style.display = 'none';
        settingsView.style.display = 'none';
        projectsView.style.display = 'none';
        modelsView.style.display = 'none';
        
        // Remove active class from all nav buttons
        chatNav.classList.remove('active');
        settingsNav.classList.remove('active');
        projectsNav.classList.remove('active');
        modelsNav.classList.remove('active');
        
        // Show selected view and set active nav button
        switch (view) {
            case 'chat':
                chatView.style.display = 'flex';
                chatNav.classList.add('active');
                break;
            case 'settings':
                settingsView.style.display = 'block';
                settingsNav.classList.add('active');
                break;
            case 'projects':
                projectsView.style.display = 'block';
                projectsNav.classList.add('active');
                break;
            case 'models':
                modelsView.style.display = 'block';
                modelsNav.classList.add('active');
                break;
        }
    }
    
    // Set initial view
    setActiveView('chat');
    
    // Navigation event listeners
    chatNav.addEventListener('click', () => setActiveView('chat'));
    settingsNav.addEventListener('click', () => setActiveView('settings'));
    projectsNav.addEventListener('click', () => setActiveView('projects'));
    modelsNav.addEventListener('click', () => setActiveView('models'));
    
    // Sidebar toggle
    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
        if (sidebar.classList.contains('collapsed')) {
            mainContent.classList.remove('ml-64');
            mainContent.classList.add('ml-0');
            sidebarToggle.innerHTML = '<span class="neon-text text-lg leading-none">▶</span>';
        } else {
            mainContent.classList.remove('ml-0');
            mainContent.classList.add('ml-64');
            sidebarToggle.innerHTML = '<span class="neon-text text-lg leading-none">◀</span>';
        }
    });
    
    // Project functions
    function renderProjects() {
        if (projects.length === 0) {
            projectsList.innerHTML = `
                <div class="text-center py-8">
                    <p class="text-gray-500">No projects yet. Create your first project to get started!</p>
                </div>
            `;
            return;
        }
        
        projectsList.innerHTML = '';
        projects.forEach((project, index) => {
            const projectCard = document.createElement('div');
            projectCard.className = 'project-card mb-4 p-4 border border-neon-blue rounded-lg bg-darker-bg';
            projectCard.innerHTML = `
                <div class="flex justify-between items-start">
                    <h3 class="text-lg font-bold text-neon-blue">${project.name}</h3>
                    <div class="flex space-x-2">
                        <button class="edit-project text-neon-blue hover:text-neon-pink" data-index="${index}">Edit</button>
                        <button class="delete-project text-red-500 hover:text-red-300" data-index="${index}">Delete</button>
                    </div>
                </div>
                <p class="mt-2 text-sm">${project.description || 'No description'}</p>
                <div class="mt-3 text-xs text-gray-400">
                    <span>Created: <span>${new Date(project.createdAt).toLocaleString()}</span></span>
                    <span class="ml-3">Updated: <span>${new Date(project.updatedAt).toLocaleString()}</span></span>
                </div>
            `;
            projectsList.appendChild(projectCard);
            
            // Add event listeners to edit and delete buttons
            projectCard.querySelector('.edit-project').addEventListener('click', () => editProject(index));
            projectCard.querySelector('.delete-project').addEventListener('click', () => deleteProject(index));
        });
    }
    
    function editProject(index) {
        if (index >= 0 && index < projects.length) {
            const project = projects[index];
            projectName.value = project.name;
            projectDescription.value = project.description || '';
            projectRules.value = project.rules || '';
            editingProjectIndex = index;
            document.getElementById('project-modal-title').textContent = 'Edit Project';
            document.getElementById('save-project-btn').textContent = 'Update Project';
            projectModal.style.display = 'flex';
        }
    }
    
    function deleteProject(index) {
        if (index >= 0 && index < projects.length) {
            if (confirm('Are you sure you want to delete "' + projects[index].name + '"?')) {
                projects.splice(index, 1);
                localStorage.setItem('tron_projects', JSON.stringify(projects));
                renderProjects();
            }
        }
    }
    
    function saveProject() {
        if (!projectName.value.trim()) {
            alert('Project name is required');
            return;
        }
        
        const project = {
            id: Date.now().toString(),
            name: projectName.value.trim(),
            description: projectDescription.value.trim(),
            rules: projectRules.value.trim(),
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
        };
        
        if (editingProjectIndex !== null) {
            // Update existing project
            project.id = projects[editingProjectIndex].id;
            project.createdAt = projects[editingProjectIndex].createdAt;
            projects[editingProjectIndex] = project;
        } else {
            // Add new project
            projects.push(project);
        }
        
        // Save to localStorage
        localStorage.setItem('tron_projects', JSON.stringify(projects));
        
        // Reset form and close modal
        projectName.value = '';
        projectDescription.value = '';
        projectRules.value = '';
        editingProjectIndex = null;
        projectModal.style.display = 'none';
        
        // Update projects list
        renderProjects();
    }
    
    // Project event listeners
    createProjectBtn.addEventListener('click', () => {
        projectName.value = '';
        projectDescription.value = '';
        projectRules.value = '';
        editingProjectIndex = null;
        document.getElementById('project-modal-title').textContent = 'Create New Project';
        document.getElementById('save-project-btn').textContent = 'Save Project';
        projectModal.style.display = 'flex';
    });
    
    saveProjectBtn.addEventListener('click', saveProject);
    
    cancelProjectBtn.addEventListener('click', () => {
        projectModal.style.display = 'none';
    });
    
    // Close modal when clicking outside
    projectModal.addEventListener('click', (e) => {
        if (e.target === projectModal) {
            projectModal.style.display = 'none';
        }
    });

    // WebSocket setup
    window.chatSocket = null;
    try {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        console.log(`app.js: Attempting to connect to WebSocket at ${wsUrl}`);
        
        window.chatSocket = new WebSocket(wsUrl);
        
        window.chatSocket.onopen = function(e) {
            console.log("app.js: WebSocket connection established");
        };
        
        window.chatSocket.onmessage = function(event) {
            try {
                const message = JSON.parse(event.data);
                console.log("app.js: Received message:", message);
                
                if (message.type === 'client_id') {
                    console.log(`app.js: Client ID received: ${message.content}`);
                    // Store client ID if needed
                    window.clientId = message.content;
                } else if (message.type === 'indicator') {
                    if (message.content === 'typing') {
                        window.showTypingIndicator();
                    } else {
                        window.hideTypingIndicator();
                    }
                } else if (message.type === 'text_delta') {
                    // Handle realtime text deltas
                    const deltaElement = document.querySelector('.realtime-response');
                    if (deltaElement) {
                        // Append to existing realtime response
                        deltaElement.textContent += message.content;
                    } else {
                        // Create new realtime response element
                        const messageElement = document.createElement('div');
                        messageElement.className = 'message message-ai realtime-response';
                        messageElement.textContent = message.content;
                        document.getElementById('chat-messages').appendChild(messageElement);
                        
                        // Scroll to bottom
                        if (chatCanvas) {
                            chatCanvas.scrollTop = chatCanvas.scrollHeight;
                        }
                    }
                } else if (message.type === 'audio_delta') {
                    // Handle realtime audio deltas
                    console.log("app.js: Received audio delta");
                    
                    // Play the audio if it's available
                    if (message.audio_data) {
                        try {
                            // Create a global audio context if it doesn't exist
                            if (!window.audioContext) {
                                const AudioContext = window.AudioContext || window.webkitAudioContext;
                                window.audioContext = new AudioContext();
                                console.log("app.js: Created global audio context");
                                
                                // Create a gain node for volume control
                                window.gainNode = window.audioContext.createGain();
                                window.gainNode.gain.value = 1.0; // Full volume
                                window.gainNode.connect(window.audioContext.destination);
                            }
                            
                            // 1. Decode Base64 to binary
                            const binaryString = atob(message.audio_data);
                            
                            // 2. Convert binary string to array buffer
                            const bytes = new Uint8Array(binaryString.length);
                            for (let i = 0; i < binaryString.length; i++) {
                                bytes[i] = binaryString.charCodeAt(i);
                            }
                            
                            // 3. Create WAV header for PCM16 audio at 24kHz
                            const wavHeader = createWavHeader(bytes.length, 1, 24000, 16);
                            
                            // 4. Concatenate WAV header with audio data
                            const audioBuffer = new Uint8Array(wavHeader.length + bytes.length);
                            audioBuffer.set(wavHeader);
                            audioBuffer.set(bytes, wavHeader.length);
                            
                            // Use Web Audio API directly for more reliable playback
                            window.audioContext.decodeAudioData(
                                audioBuffer.buffer,
                                (decodedBuffer) => {
                                    console.log("app.js: Audio decoded successfully with Web Audio API");
                                    
                                    // Create a buffer source node
                                    const source = window.audioContext.createBufferSource();
                                    source.buffer = decodedBuffer;
                                    
                                    // Connect to the gain node (which is connected to the destination)
                                    source.connect(window.gainNode);
                                    
                                    // Play the audio
                                    source.start(0);
                                    console.log("app.js: Audio playback started with Web Audio API");
                                    
                                    // Handle completion
                                    source.onended = () => {
                                        console.log("app.js: Audio playback ended");
                                    };
                                },
                                (error) => {
                                    console.error("app.js: Error decoding audio:", error);
                                    
                                    // Fallback to Audio element if Web Audio API fails
                                    try {
                                        // Create blob with WAV format
                                        const audioBlob = new Blob([audioBuffer], { type: 'audio/wav' });
                                        const audioUrl = URL.createObjectURL(audioBlob);
                                        
                                        // Create and configure audio element
                                        const audioElement = new Audio(audioUrl);
                                        audioElement.volume = 1.0;
                                        
                                        // Add event listeners for debugging
                                        audioElement.addEventListener('play', () => {
                                            console.log("app.js: Audio playback started with Audio element");
                                        });
                                        
                                        audioElement.addEventListener('ended', () => {
                                            console.log("app.js: Audio playback ended");
                                            // Clean up the URL object to prevent memory leaks
                                            URL.revokeObjectURL(audioUrl);
                                        });
                                        
                                        audioElement.addEventListener('error', (e) => {
                                            console.error("app.js: Audio playback error:", e);
                                        });
                                        
                                        // Play the audio
                                        audioElement.play()
                                            .then(() => {
                                                console.log("app.js: Audio playback started successfully with Audio element");
                                            })
                                            .catch(e => {
                                                console.error("app.js: Error playing audio with Audio element:", e);
                                            });
                                    } catch (audioElementErr) {
                                        console.error("app.js: Audio element fallback error:", audioElementErr);
                                    }
                                }
                            );
                        } catch (e) {
                            console.error("app.js: Error processing audio delta:", e);
                        }
                    }
                } else if (message.type === 'response_done') {
                    // Handle completion of realtime response
                    console.log("app.js: Realtime response complete");
                    
                    // Convert the realtime response to a regular message
                    const deltaElement = document.querySelector('.realtime-response');
                    if (deltaElement) {
                        // Remove the realtime-response class
                        deltaElement.classList.remove('realtime-response');
                        
                        // Format with markdown
                        deltaElement.innerHTML = formatMessageContent(deltaElement.textContent);
                    }
                } else if (message.type === 'transcription') {
                    // Display transcription as a system message
                    const transcriptionMsg = {
                        role: 'system',
                        content: message.content,
                        type: 'text',
                        timestamp: message.timestamp
                    };
                    window.displayMessage(transcriptionMsg, false);
                } else if (message.role === 'assistant') {
                    window.hideTypingIndicator();
                    window.displayMessage(message, true);
                    
                    // Save message to history
                    try {
                        const savedHistory = localStorage.getItem('chat_history') || '[]';
                        const history = JSON.parse(savedHistory);
                        if (Array.isArray(history)) {
                            // Add the new message
                            history.push(message);
                            // Limit history to last 100 messages to prevent localStorage overflow
                            const limitedHistory = history.slice(-100);
                            localStorage.setItem('chat_history', JSON.stringify(limitedHistory));
                        }
                    } catch (e) {
                        console.error("app.js: Error saving message to history:", e);
                    }
                }
            } catch (e) {
                console.error("app.js: Error processing WebSocket message:", e);
            }
        };
        
        window.chatSocket.onclose = function(event) {
            if (event.wasClean) {
                console.log(`app.js: WebSocket connection closed cleanly, code=${event.code}, reason=${event.reason}`);
            } else {
                console.error('app.js: WebSocket connection died');
            }
        };
        
        window.chatSocket.onerror = function(error) {
            console.error(`app.js: WebSocket error: ${error.message}`);
        };
    } catch (error) {
        console.error("app.js: Error setting up WebSocket:", error);
    }

    // Typing indicator setup
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator hidden';
    typingIndicator.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <span>AI is typing...</span>
    `;
    if (chatMessagesContainer) {
        chatMessagesContainer.appendChild(typingIndicator);
        console.log("app.js: Typing indicator added to chat messages container");
    }
    else console.error("Could not find #chat-messages for indicator.");

    // Attach basic listeners managed by standard JS
    if (chatInput && chatInput.tagName.toLowerCase() === 'textarea') {
        chatInput.addEventListener('input', autoResizeInput, false);
        chatInput.addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); window.sendMessage(); } });
        // Add paste event listener for clipboard images
        chatInput.addEventListener('paste', handlePastedImage);
    }
    if (sendButton) { sendButton.addEventListener('click', () => { window.sendMessage(); }); }
    
    // File input change handler
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            console.log("app.js: File selected:", file.name, file.type, file.size);
            
            // Accept all file types
            // We'll handle different file types differently
            const isImage = file.type.startsWith('image/');
            
            if (!isImage) {
                console.log("app.js: Non-image file selected, will be sent as attachment");
            }
            
            // Store the file for later use
            currentImage = file;
            
            // Show preview
            const reader = new FileReader();
            reader.onload = (event) => {
                previewImage.src = event.target.result;
                imagePreview.classList.remove('hidden');
                console.log("app.js: Image preview loaded");
            };
            reader.onerror = (error) => {
                console.error("app.js: Error reading file:", error);
                alert('Error loading image preview. Please try again.');
            };
            reader.readAsDataURL(file);
        });
    }
    
    // Clear image button
    if (clearImageButton) {
        clearImageButton.addEventListener('click', () => {
            currentImage = null;
            fileInput.value = '';
            imagePreview.classList.add('hidden');
        });
    }
    
    // Clear chat history button
    if (clearHistoryButton) {
        clearHistoryButton.addEventListener('click', () => {
            if (confirm('Are you sure you want to clear all chat history? This cannot be undone.')) {
                // Clear localStorage
                localStorage.removeItem('chat_history');
                
                // Clear chat messages from DOM
                if (chatMessagesContainer) {
                    chatMessagesContainer.innerHTML = '';
                    
                    // Add system message
                    const systemMessage = {
                        role: 'system',
                        content: 'Chat history has been cleared.',
                        type: 'text',
                        timestamp: new Date().toISOString()
                    };
                    window.displayMessage(systemMessage, false);
                }
                
                console.log("app.js: Chat history cleared");
            }
        });
    }
    
    // Initialize settings
    if (voiceEnabledSetting) voiceEnabledSetting.checked = voiceEnabled;
    const conversationalModeSetting = document.getElementById('conversational-mode-setting');
    if (conversationalModeSetting) conversationalModeSetting.checked = conversationalMode;
    const conversationModeSetting = document.getElementById('conversation-mode-setting');
    if (conversationModeSetting) conversationModeSetting.value = conversationMode;
    if (voiceTypeSetting) voiceTypeSetting.value = selectedVoice;
    if (voiceSpeedSetting) {
        voiceSpeedSetting.value = voiceSpeed;
        if (voiceSpeedValue) voiceSpeedValue.textContent = `${voiceSpeed}x`;
    }
    if (imageSizeSetting) imageSizeSetting.value = defaultImageSize;
    if (imageQualitySetting) imageQualitySetting.value = defaultImageQuality;
    if (imageStyleSetting) imageStyleSetting.value = defaultImageStyle;
    
    // Settings event listeners
    if (voiceEnabledSetting) {
        voiceEnabledSetting.addEventListener('change', () => {
            voiceEnabled = voiceEnabledSetting.checked;
            localStorage.setItem('voice_enabled', voiceEnabled);
        });
    }
    
    if (conversationalModeSetting) {
        conversationalModeSetting.addEventListener('change', () => {
            conversationalMode = conversationalModeSetting.checked;
            localStorage.setItem('conversational_mode', conversationalMode);
        });
    }
    
    if (conversationModeSetting) {
        conversationModeSetting.addEventListener('change', () => {
            conversationMode = conversationModeSetting.value;
            localStorage.setItem('conversation_mode', conversationMode);
        });
    }
    
    if (voiceTypeSetting) {
        voiceTypeSetting.addEventListener('change', () => {
            selectedVoice = voiceTypeSetting.value;
            localStorage.setItem('selected_voice', selectedVoice);
        });
    }
    
    if (voiceSpeedSetting) {
        voiceSpeedSetting.addEventListener('input', () => {
            voiceSpeed = parseFloat(voiceSpeedSetting.value);
            if (voiceSpeedValue) voiceSpeedValue.textContent = `${voiceSpeed.toFixed(1)}x`;
            localStorage.setItem('voice_speed', voiceSpeed);
        });
    }
    
    if (imageSizeSetting) {
        imageSizeSetting.addEventListener('change', () => {
            defaultImageSize = imageSizeSetting.value;
            localStorage.setItem('image_size', defaultImageSize);
        });
    }
    
    if (imageQualitySetting) {
        imageQualitySetting.addEventListener('change', () => {
            defaultImageQuality = imageQualitySetting.value;
            localStorage.setItem('image_quality', defaultImageQuality);
        });
    }
    
    if (imageStyleSetting) {
        imageStyleSetting.addEventListener('change', () => {
            defaultImageStyle = imageStyleSetting.value;
            localStorage.setItem('image_style', defaultImageStyle);
        });
    }
    
    // Voice recording functionality
    if (voiceRecordBtn) {
        voiceRecordBtn.addEventListener('click', toggleRecording);
    }
    
    if (stopRecordingBtn) {
        stopRecordingBtn.addEventListener('click', stopRecording);
    }
    
    async function toggleRecording() {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            stopRecording();
            return;
        }
        
        try {
            // First, check if the user has granted microphone permissions
            const permissionStatus = await navigator.permissions.query({ name: 'microphone' });
            if (permissionStatus.state === 'denied') {
                alert("Microphone access is denied. Please allow microphone access in your browser settings and try again.");
                return;
            }
            
            // Request audio with specific constraints for better compatibility
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    channelCount: 1,          // Mono audio
                    sampleRate: 44100,        // Standard sample rate
                    echoCancellation: true,   // Reduce echo
                    noiseSuppression: true    // Reduce background noise
                } 
            });
            
            // Prioritize formats that OpenAI supports directly
            const supportedMimeTypes = [
                'audio/mp3',
                'audio/mpeg',
                'audio/mp4',
                'audio/wav',
                'audio/webm',
                'audio/ogg'
            ];
            
            let selectedMimeType = null;
            for (const mimeType of supportedMimeTypes) {
                if (MediaRecorder.isTypeSupported(mimeType)) {
                    selectedMimeType = mimeType;
                    console.log(`app.js: Found supported MIME type: ${mimeType}`);
                    break;
                }
            }
            
            if (!selectedMimeType) {
                console.warn("app.js: No supported MIME types found, using default");
                selectedMimeType = '';  // Use default
            }
            
            // Create MediaRecorder with the selected MIME type
            const options = selectedMimeType ? { mimeType: selectedMimeType } : {};
            mediaRecorder = new MediaRecorder(stream, options);
            audioChunks = [];
            
            console.log(`app.js: MediaRecorder created with MIME type: ${mediaRecorder.mimeType}`);
            
            // Set up continuous recording with smaller chunks
            mediaRecorder.addEventListener('dataavailable', event => {
                audioChunks.push(event.data);
                console.log(`app.js: Audio chunk received, size: ${event.data.size} bytes, type: ${event.data.type}`);
                
                // Process audio chunks in real-time if we have enough data
                if (audioChunks.length >= 3) {  // Process after collecting a few chunks
                    processAudioChunks();
                }
            });
            
            mediaRecorder.addEventListener('stop', finalizeAudioRecording);
            
            // Start recording with smaller timeslice (200ms chunks)
            mediaRecorder.start(200);  // Get data every 200ms for more real-time experience
            voiceRecordBtn.classList.add('recording');
            recordingIndicator.classList.remove('hidden');
            
            // Start timer
            recordingSeconds = 0;
            updateRecordingTime();
            recordingTimer = setInterval(updateRecordingTime, 1000);
            
            console.log(`app.js: Voice recording started with MIME type: ${mediaRecorder.mimeType}`);
        } catch (error) {
            console.error("app.js: Error starting voice recording:", error);
            
            if (error.name === 'NotAllowedError') {
                alert("Microphone access was denied. Please allow microphone access in your browser settings and try again.");
            } else {
                alert("Could not access microphone. Error: " + error.message);
            }
        }
    }
    
    function updateRecordingTime() {
        recordingSeconds++;
        const minutes = Math.floor(recordingSeconds / 60);
        const seconds = recordingSeconds % 60;
        recordingTimeDisplay.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        
        // Auto-stop after 2 minutes to prevent very large files
        if (recordingSeconds >= 120) {
            stopRecording();
        }
    }
    
    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
            voiceRecordBtn.classList.remove('recording');
            recordingIndicator.classList.add('hidden');
            clearInterval(recordingTimer);
            
            // Stop all tracks on the stream
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
            
            console.log("app.js: Voice recording stopped");
        }
    }
    
    // Process audio chunks in real-time during recording
    async function processAudioChunks() {
        if (audioChunks.length === 0) return;
        
        try {
            // Create a temporary blob from current chunks
            // Use wav MIME type to ensure compatibility with OpenAI's transcription API
            const tempBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const reader = new FileReader();
            
            reader.onload = async (event) => {
                const audioBase64 = event.target.result;
                
                // Send to server for real-time processing without showing UI elements
                try {
                    // Get default model
                    let modelId = 'gpt-4o-mini';
                    
                    // Create message to send
                    const audioMessage = {
                        type: 'audio',
                        role: 'user',
                        audio_data: audioBase64,
                        tts_enabled: voiceEnabled,
                        conversational_mode: conversationalMode,
                        conversation_mode: conversationMode,
                        voice: selectedVoice,
                        speed: voiceSpeed,
                        audio_format: 'wav',  // Explicitly set to wav for compatibility
                        timestamp: new Date().toISOString(),
                        model_id: modelId,
                        provider: "OpenAI"
                    };
                    
                    // Log the MIME type being used
                    console.log("app.js: Audio MIME type:", tempBlob.type);
                    
                    // Send to server
                    window.chatSocket.send(JSON.stringify(audioMessage));
                    console.log("app.js: Real-time audio chunk sent to server");
                    
                    // Clear the chunks after sending to avoid duplicate processing
                    audioChunks = [];
                } catch (e) {
                    console.error("app.js: Error sending real-time audio chunk:", e);
                }
            };
            
            reader.readAsDataURL(tempBlob);
        } catch (error) {
            console.error("app.js: Error processing real-time audio chunks:", error);
        }
    }
    
    // Finalize audio recording when stopped
    async function finalizeAudioRecording() {
        console.log("app.js: Finalizing audio recording");
        
        // No need to send the audio again as we've been sending chunks in real-time
        // Just clean up and prepare for the next recording
        audioChunks = [];
    }
    
    // Image generation functionality
    if (generateImageBtn) {
        generateImageBtn.addEventListener('click', () => {
            // Set default values from settings
            if (imageSizeSelect) imageSizeSelect.value = defaultImageSize;
            if (imageQualitySelect) imageQualitySelect.value = defaultImageQuality;
            if (imageStyleSelect) imageStyleSelect.value = defaultImageStyle;
            
            // Clear previous prompt
            if (imagePromptInput) imagePromptInput.value = '';
            
            // Show modal
            if (imageGenModal) imageGenModal.style.display = 'flex';
        });
    }
    
    if (cancelImageBtn) {
        cancelImageBtn.addEventListener('click', () => {
            if (imageGenModal) imageGenModal.style.display = 'none';
        });
    }
    
    // Close modal when clicking outside
    if (imageGenModal) {
        imageGenModal.addEventListener('click', (e) => {
            if (e.target === imageGenModal) {
                imageGenModal.style.display = 'none';
            }
        });
    }
    
    if (generateImageSubmitBtn) {
        generateImageSubmitBtn.addEventListener('click', () => {
            const prompt = imagePromptInput.value.trim();
            if (!prompt) {
                alert('Please enter a prompt for the image generation');
                return;
            }
            
            // Get settings
            const size = imageSizeSelect.value;
            const quality = imageQualitySelect.value;
            const style = imageStyleSelect.value;
            
            // Hide modal
            imageGenModal.style.display = 'none';
            
            // Show typing indicator
            window.showTypingIndicator();
            
            // Create message to send
            const imageGenMessage = {
                type: 'generate_image',
                prompt: prompt,
                size: size,
                quality: quality,
                style: style,
                timestamp: new Date().toISOString(),
                model_id: 'dall-e-3',
                provider: "OpenAI"
            };
            
            // Display user message
            const userMessage = {
                role: 'user',
                type: 'text',
                content: `Generating image: ${prompt}`,
                timestamp: new Date().toISOString()
            };
            window.displayMessage(userMessage, false);
            
            // Send to server
            try {
                window.chatSocket.send(JSON.stringify(imageGenMessage));
                console.log("app.js: Image generation request sent to server");
            } catch (e) {
                console.error("app.js: Error sending image generation request:", e);
                window.hideTypingIndicator();
            }
        });
    }
    
    // Send message function
    window.sendMessage = () => {
        const localChatInput = document.getElementById('chat-input');
        if (!localChatInput || !window.chatSocket || window.chatSocket.readyState !== WebSocket.OPEN) {
            console.error("app.js: Cannot send message - chat input or WebSocket not available");
            return;
        }
        
        const text = localChatInput.value.trim();
        
        // If no text and no image, don't send
        if (!text && !currentImage) return;
        
        // Show typing indicator while processing
        window.showTypingIndicator();
        
        // Default model
        let modelId = 'gpt-4o-mini';
        
        if (currentImage) {
            const isImage = currentImage.type.startsWith('image/');
            console.log(`app.js: Sending ${isImage ? 'image' : 'file'} message with${text ? ' caption' : 'out caption'}`);
            
            // Handle file message
            const reader = new FileReader();
            reader.onload = (event) => {
                const fileMessage = {
                    type: isImage ? 'image' : 'file',
                    role: 'user',
                    content: event.target.result,
                    caption: text, // Use text as caption if provided
                    filename: currentImage.name,
                    filetype: currentImage.type,
                    filesize: currentImage.size,
                    timestamp: new Date().toISOString(),
                    model_id: modelId,
                    provider: "OpenAI"
                };
                
                // Display in chat
                if (isImage) {
                    window.displayMessage(fileMessage, false);
                } else {
                    // For non-image files, create a custom message
                    const fileDisplayMessage = {
                        role: 'user',
                        type: 'text',
                        content: `File attached: ${currentImage.name} (${(currentImage.size / 1024).toFixed(1)} KB)${text ? '<br>' + text : ''}`,
                        timestamp: new Date().toISOString()
                    };
                    window.displayMessage(fileDisplayMessage, false);
                }
                
                // Send to server
                try {
                    window.chatSocket.send(JSON.stringify(fileMessage));
                    console.log(`app.js: ${isImage ? 'Image' : 'File'} message sent to server`);
                } catch (e) {
                    console.error(`app.js: Error sending ${isImage ? 'image' : 'file'} message:`, e);
                    window.hideTypingIndicator();
                }
                
                // Clear input
                localChatInput.value = '';
                currentImage = null;
                fileInput.value = '';
                imagePreview.classList.add('hidden');
                setTimeout(() => autoResizeInput.call(localChatInput), 0);
            };
            reader.readAsDataURL(currentImage);
        } else {
            console.log("app.js: Sending text message");
            // Regular text message
            const userMessage = { type: 'text', role: 'user', content: text, timestamp: new Date().toISOString() };
            const messageToSend = { ...userMessage, model_id: modelId, provider: "OpenAI" };
            
            try {
                window.chatSocket.send(JSON.stringify(messageToSend));
                console.log("app.js: Text message sent to server");
            } catch (e) {
                console.error("app.js: Error sending text message:", e);
                window.hideTypingIndicator();
            }
            
            window.displayMessage(userMessage, false);
            
            // Save user message to history
            try {
                const savedHistory = localStorage.getItem('chat_history') || '[]';
                const history = JSON.parse(savedHistory);
                if (Array.isArray(history)) {
                    history.push(userMessage);
                    const limitedHistory = history.slice(-100);
                    localStorage.setItem('chat_history', JSON.stringify(limitedHistory));
                }
            } catch (e) {
                console.error("app.js: Error saving user message to history:", e);
            }
            
            localChatInput.value = '';
            setTimeout(() => autoResizeInput.call(localChatInput), 0);
        }
    };

    // Initial history load
    try {
        const savedHistory = localStorage.getItem('chat_history');
        if (savedHistory) {
            const history = JSON.parse(savedHistory);
            if (Array.isArray(history) && history.length > 0) {
                console.log(`app.js: Loading ${history.length} messages from history`);
                history.forEach(msg => {
                    if (msg && msg.role && msg.content) {
                        window.displayMessage(msg, false);
                    }
                });
            }
        }
    } catch (e) {
        console.error("app.js: Error loading chat history:", e);
    }

}); // End DOMContentLoaded

console.log("app.js: End of script");
