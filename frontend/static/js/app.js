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
function autoResizeInput() { if (!this || typeof this.scrollHeight === 'undefined') return; this.style.height = 'auto'; const newHeight = this.scrollHeight; const minHeight = 40; this.style.height = Math.max(minHeight, newHeight) + 'px'; }
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
    }
    if (sendButton) { sendButton.addEventListener('click', () => { window.sendMessage(); }); }
    
    // File input change handler
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            // Check if file is an image
            if (!file.type.startsWith('image/')) {
                alert('Please select an image file.');
                return;
            }
            
            // Store the file for later use
            currentImage = file;
            
            // Show preview
            const reader = new FileReader();
            reader.onload = (event) => {
                previewImage.src = event.target.result;
                imagePreview.classList.remove('hidden');
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
        if (!localChatInput || !window.chatSocket || window.chatSocket.readyState !== WebSocket.OPEN) return;
        
        const text = localChatInput.value.trim();
        
        // If no text and no image, don't send
        if (!text && !currentImage) return;
        
        // Default model
        let modelId = 'gpt-4o-mini';
        
        if (currentImage) {
            // Handle image message
            const reader = new FileReader();
            reader.onload = (event) => {
                const imageMessage = {
                    type: 'image',
                    role: 'user',
                    content: event.target.result,
                    caption: text, // Use text as caption if provided
                    timestamp: new Date().toISOString(),
                    model_id: modelId,
                    provider: "OpenAI"
                };
                
                // Display image in chat
                window.displayMessage(imageMessage, false);
                
                // Send to server
                window.chatSocket.send(JSON.stringify(imageMessage));
                
                // Clear input
                localChatInput.value = '';
                currentImage = null;
                fileInput.value = '';
                imagePreview.classList.add('hidden');
                setTimeout(() => autoResizeInput.call(localChatInput), 0);
            };
            reader.readAsDataURL(currentImage);
        } else {
            // Regular text message
            const userMessage = { type: 'text', role: 'user', content: text, timestamp: new Date().toISOString() };
            const messageToSend = { ...userMessage, model_id: modelId, provider: "OpenAI" };
            window.chatSocket.send(JSON.stringify(messageToSend));
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
