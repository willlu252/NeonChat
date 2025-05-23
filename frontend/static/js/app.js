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
function formatMessageContent(content) { 
    if (!content) return ''; 
    try { 
        return marked.parse(content || ''); 
    } catch (e) { 
        console.error("Markdown error:", e); 
        return content; 
    } 
}

window.displayMessage = (message, useTypewriter = false) => {
     const localChatMessages = document.getElementById('chat-messages');
     if (!localChatMessages || !message || !message.role) return;
     const messageElement = document.createElement('div');
     messageElement.className = `message ${message.role === 'user' ? 'message-user' : 'message-ai'}`;
     if (message.role === 'system') { 
         messageElement.classList.add('message-system'); 
         messageElement.classList.remove('message-ai'); 
     }
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
     else if (useTypewriter && message.role === 'assistant') { 
         messageElement.classList.add('typewriter'); 
         typewriterEffect(messageElement, message.content || ''); 
     }
     else { 
         messageElement.innerHTML = formatMessageContent(message.content || ''); 
     }
     localChatMessages.appendChild(messageElement);
     requestAnimationFrame(() => { 
         if (chatCanvas) chatCanvas.scrollTop = chatCanvas.scrollHeight; 
     });
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
    const maxHeight = 150;
    
    // Set the height within min and max constraints
    this.style.height = Math.min(Math.max(minHeight, newHeight), maxHeight) + 'px';
    
    // Enable or disable scrolling based on content height
    this.style.overflowY = newHeight > maxHeight ? 'auto' : 'hidden';
}

window.showTypingIndicator = () => { 
    const el = document.querySelector('.typing-indicator'); 
    if (el) el.classList.remove('hidden'); 
};

window.hideTypingIndicator = () => { 
    const el = document.querySelector('.typing-indicator'); 
    if (el) el.classList.add('hidden'); 
};

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
    
    // Navigation elements
    const chatNav = document.getElementById('chat-nav');
    const settingsNav = document.getElementById('settings-nav');
    const projectsNav = document.getElementById('projects-nav');
    
    // View elements
    const chatView = document.getElementById('chat-view');
    const settingsView = document.getElementById('settings-view');
    const projectsView = document.getElementById('projects-view');
    
    // Sidebar elements (no longer toggle-able)
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
        
        // Remove active class from all nav buttons
        chatNav.classList.remove('active');
        settingsNav.classList.remove('active');
        projectsNav.classList.remove('active');
        
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
        }
    }
    
    // Set initial view
    setActiveView('chat');
    
    // Navigation event listeners
    chatNav.addEventListener('click', () => setActiveView('chat'));
    settingsNav.addEventListener('click', () => setActiveView('settings'));
    projectsNav.addEventListener('click', () => setActiveView('projects'));
    
    // Sidebar toggle functionality removed - sidebar is now static
    
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
        const wsUrl = `${protocol}//localhost:8000/ws`;
        console.log(`app.js: Attempting to connect to WebSocket at ${wsUrl}`);
        
        window.chatSocket = new WebSocket(wsUrl);
        
        window.chatSocket.onopen = function(e) {
            console.log("app.js: WebSocket connection established");
        };
        
        // Track streaming state
        let currentStreamingMessage = null;
        let streamingElement = null;
        
        window.chatSocket.onmessage = function(event) {
            try {
                const message = JSON.parse(event.data);
                console.log("app.js: Received message:", message);
                
                if (message.type === 'client_id') {
                    console.log(`app.js: Client ID received: ${message.content}`);
                    window.clientId = message.content;
                } else if (message.type === 'indicator') {
                    if (message.content === 'typing') {
                        window.showTypingIndicator();
                    } else {
                        window.hideTypingIndicator();
                    }
                } else if (message.type === 'text_chunk') {
                    // Handle streaming text chunks
                    window.hideTypingIndicator();
                    
                    if (!currentStreamingMessage) {
                        // Start new streaming message
                        currentStreamingMessage = {
                            role: 'assistant',
                            content: '',
                            type: 'text',
                            timestamp: new Date().toISOString()
                        };
                        
                        // Create streaming element
                        streamingElement = document.createElement('div');
                        streamingElement.className = 'message message-ai streaming-response';
                        streamingElement.innerHTML = '<span class="streaming-cursor">|</span>';
                        document.getElementById('chat-messages').appendChild(streamingElement);
                        
                        // Add CSS for blinking cursor if not already present
                        if (!document.querySelector('#streaming-cursor-style')) {
                            const style = document.createElement('style');
                            style.id = 'streaming-cursor-style';
                            style.textContent = `
                                .streaming-cursor {
                                    animation: blink 1s infinite;
                                    color: #00ffff;
                                }
                                @keyframes blink {
                                    0%, 50% { opacity: 1; }
                                    51%, 100% { opacity: 0; }
                                }
                            `;
                            document.head.appendChild(style);
                        }
                    }
                    
                    // Append new content
                    currentStreamingMessage.content += message.content || '';
                    
                    // Update display with cursor
                    if (streamingElement) {
                        streamingElement.innerHTML = formatMessageContent(currentStreamingMessage.content) + 
                                                   '<span class="streaming-cursor">|</span>';
                        
                        // Scroll to bottom
                        if (chatCanvas) {
                            chatCanvas.scrollTop = chatCanvas.scrollHeight;
                        }
                    }
                } else if (message.done === true || message.type === 'response_done') {
                    // Complete the streaming message
                    if (currentStreamingMessage && streamingElement) {
                        // Remove cursor and finalize message
                        streamingElement.innerHTML = formatMessageContent(currentStreamingMessage.content);
                        streamingElement.classList.remove('streaming-response');
                        
                        // Save complete message to history
                        try {
                            const savedHistory = localStorage.getItem('chat_history') || '[]';
                            const history = JSON.parse(savedHistory);
                            if (Array.isArray(history)) {
                                history.push(currentStreamingMessage);
                                const limitedHistory = history.slice(-100);
                                localStorage.setItem('chat_history', JSON.stringify(limitedHistory));
                            }
                        } catch (e) {
                            console.error("app.js: Error saving message to history:", e);
                        }
                        
                        // Reset streaming state
                        currentStreamingMessage = null;
                        streamingElement = null;
                        
                        console.log("app.js: Streaming response completed");
                    }
                } else if (message.type === 'text_delta') {
                    // Handle legacy realtime text deltas (fallback)
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
                } else if (message.role === 'assistant') {
                    // Handle complete non-streaming messages (fallback)
                    window.hideTypingIndicator();
                    
                    // Only display if not currently streaming
                    if (!currentStreamingMessage) {
                        window.displayMessage(message, true);
                        
                        // Save message to history
                        try {
                            const savedHistory = localStorage.getItem('chat_history') || '[]';
                            const history = JSON.parse(savedHistory);
                            if (Array.isArray(history)) {
                                history.push(message);
                                const limitedHistory = history.slice(-100);
                                localStorage.setItem('chat_history', JSON.stringify(limitedHistory));
                            }
                        } catch (e) {
                            console.error("app.js: Error saving message to history:", e);
                        }
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

    // Attach basic listeners
    if (chatInput && chatInput.tagName.toLowerCase() === 'textarea') {
        chatInput.addEventListener('input', autoResizeInput, false);
        chatInput.addEventListener('keydown', (e) => { 
            if (e.key === 'Enter' && !e.shiftKey) { 
                e.preventDefault(); 
                window.sendMessage(); 
            } 
        });
        // Add paste event listener for clipboard images
        chatInput.addEventListener('paste', handlePastedImage);
    }
    if (sendButton) { 
        sendButton.addEventListener('click', () => { 
            window.sendMessage(); 
        }); 
    }
    
    // File input change handler
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            console.log("app.js: File selected:", file.name, file.type, file.size);
            
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
                    caption: text,
                    filename: currentImage.name,
                    filetype: currentImage.type,
                    filesize: currentImage.size,
                    timestamp: new Date().toISOString(),
                    model_id: 'claude-3-7-sonnet-20250219',
                    provider: "Claude"
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
            const userMessage = { 
                type: 'text', 
                role: 'user', 
                content: text, 
                timestamp: new Date().toISOString() 
            };
            const messageToSend = { 
                ...userMessage, 
                model_id: 'claude-3-7-sonnet-20250219', 
                provider: "Claude" 
            };
            
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