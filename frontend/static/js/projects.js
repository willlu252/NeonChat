// Projects Management Module
console.log("projects.js: Loading projects module");

class ProjectsManager {
    constructor() {
        console.log("projects.js: ProjectsManager constructor called");
        this.projects = [];
        this.currentProject = null;
        this.currentProjectFiles = [];
        this.projectChatSocket = null;
        this.projectChatMessages = [];
        this.isInWorkspace = false;
        
        this.init();
    }
    
    init() {
        console.log("projects.js: Initializing ProjectsManager");
        this.loadProjects();
        this.bindEvents();
        this.setupProjectWorkspace();
        console.log("projects.js: ProjectsManager initialization complete");
    }
    
    // Load projects from localStorage
    loadProjects() {
        try {
            const saved = localStorage.getItem('projects_data');
            if (saved) {
                this.projects = JSON.parse(saved);
            }
        } catch (e) {
            console.error("Error loading projects:", e);
            this.projects = [];
        }
    }
    
    // Save projects to localStorage
    saveProjects() {
        try {
            localStorage.setItem('projects_data', JSON.stringify(this.projects));
        } catch (e) {
            console.error("Error saving projects:", e);
        }
    }
    
    // Bind all event listeners
    bindEvents() {
        // Create project button
        const createBtn = document.getElementById('create-project-btn');
        if (createBtn) {
            console.log("projects.js: Binding create project button");
            createBtn.addEventListener('click', () => {
                console.log("projects.js: Create project button clicked");
                this.showProjectModal();
            });
        } else {
            console.error("projects.js: Create project button not found");
        }
        
        // Project modal events
        const saveBtn = document.getElementById('save-project-btn');
        const cancelBtn = document.getElementById('cancel-project-btn');
        const modal = document.getElementById('project-modal');
        
        if (saveBtn) saveBtn.addEventListener('click', () => this.saveProject());
        if (cancelBtn) cancelBtn.addEventListener('click', () => this.hideProjectModal());
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) this.hideProjectModal();
            });
        }
        
        // Back to projects button
        const backBtn = document.getElementById('back-to-projects');
        if (backBtn) {
            backBtn.addEventListener('click', () => this.showProjectsList());
        }
        
        // Project actions - removed delete button from workspace sidebar
        
        // System instructions events
        const editSystemBtn = document.getElementById('edit-system-prompt');
        const systemModal = document.getElementById('system-instructions-modal');
        const saveSystemBtn = document.getElementById('save-system-instructions-btn');
        const cancelSystemBtn = document.getElementById('cancel-system-instructions-btn');
        
        if (editSystemBtn) editSystemBtn.addEventListener('click', () => this.showSystemInstructionsModal());
        if (saveSystemBtn) saveSystemBtn.addEventListener('click', () => this.saveSystemInstructions());
        if (cancelSystemBtn) cancelSystemBtn.addEventListener('click', () => this.hideSystemInstructionsModal());
        if (systemModal) {
            systemModal.addEventListener('click', (e) => {
                if (e.target === systemModal) this.hideSystemInstructionsModal();
            });
        }
        
        // File upload events
        this.setupFileUpload();
        
        // Project chat events
        this.setupProjectChat();
    }
    
    // Setup file upload functionality
    setupFileUpload() {
        const uploadArea = document.getElementById('file-upload-area');
        const fileInput = document.getElementById('project-file-input');
        
        if (uploadArea && fileInput) {
            // Click to upload
            uploadArea.addEventListener('click', () => fileInput.click());
            
            // File selection
            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    this.handleFileUpload(Array.from(e.target.files));
                }
            });
            
            // Drag and drop
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });
            
            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('dragover');
            });
            
            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                
                const files = Array.from(e.dataTransfer.files);
                if (files.length > 0) {
                    this.handleFileUpload(files);
                }
            });
        }
    }
    
    // Setup project chat functionality
    setupProjectChat() {
        const chatInput = document.getElementById('project-chat-input');
        const sendBtn = document.getElementById('project-send-button');
        const fileInputChat = document.getElementById('project-file-input-chat');
        const imagePreview = document.getElementById('project-image-preview');
        const clearImageBtn = document.getElementById('clear-project-image');
        
        if (chatInput) {
            chatInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendProjectMessage();
                }
            });
            
            chatInput.addEventListener('input', this.autoResizeTextarea.bind(chatInput));
        }
        
        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendProjectMessage());
        }
        
        if (fileInputChat) {
            fileInputChat.addEventListener('change', (e) => {
                if (e.target.files[0]) {
                    this.previewChatImage(e.target.files[0]);
                }
            });
        }
        
        if (clearImageBtn) {
            clearImageBtn.addEventListener('click', () => {
                this.clearChatImagePreview();
            });
        }
    }
    
    // Auto-resize textarea
    autoResizeTextarea() {
        this.style.height = 'auto';
        const newHeight = this.scrollHeight;
        const minHeight = 68; // Increased to match CSS min-height for 2.5 lines
        const maxHeight = 150;
        
        this.style.height = Math.min(Math.max(minHeight, newHeight), maxHeight) + 'px';
        this.style.overflowY = newHeight > maxHeight ? 'auto' : 'hidden';
    }
    
    // Render projects list
    renderProjectsList() {
        const container = document.getElementById('projects-list');
        if (!container) return;
        
        if (this.projects.length === 0) {
            container.innerHTML = `
                <div class="text-center py-8">
                    <p class="text-gray-500">No projects yet. Create your first project to get started!</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = '';
        
        this.projects.forEach((project, index) => {
            const card = document.createElement('div');
            card.className = 'project-card mb-4';
            card.innerHTML = `
                <div class="flex justify-between items-start">
                    <div class="flex-1">
                        <h3 class="text-neon-blue font-bold text-lg mb-2">${this.escapeHtml(project.name)}</h3>
                        <p class="text-gray-300 text-sm mb-3">${this.escapeHtml(project.description || 'No description')}</p>
                        <div class="text-xs text-gray-500">
                            <span>Created: ${new Date(project.createdAt).toLocaleDateString()}</span>
                            ${project.files ? `<span class="ml-3">${project.files.length} files</span>` : ''}
                        </div>
                    </div>
                    <div class="flex space-x-2">
                        <button class="tron-button-secondary text-xs open-project" data-index="${index}">
                            Open
                        </button>
                        <button class="tron-button-secondary text-xs edit-project" data-index="${index}">
                            Edit
                        </button>
                        <button class="tron-button-danger text-xs delete-project" data-index="${index}">
                            Delete
                        </button>
                    </div>
                </div>
            `;
            
            container.appendChild(card);
            
            // Bind events for this card
            card.querySelector('.open-project').addEventListener('click', () => this.openProject(index));
            card.querySelector('.edit-project').addEventListener('click', () => this.editProject(index));
            card.querySelector('.delete-project').addEventListener('click', () => this.deleteProject(index));
        });
    }
    
    // Show/hide project modal
    showProjectModal(editIndex = null) {
        console.log("projects.js: showProjectModal called with editIndex:", editIndex);
        const modal = document.getElementById('project-modal');
        const title = document.getElementById('project-modal-title');
        const nameInput = document.getElementById('project-name');
        const descInput = document.getElementById('project-description');
        const saveBtn = document.getElementById('save-project-btn');
        
        if (!modal) {
            console.error("projects.js: Project modal not found!");
            return;
        }
        
        if (editIndex !== null && this.projects[editIndex]) {
            const project = this.projects[editIndex];
            title.textContent = 'Edit Project';
            nameInput.value = project.name;
            descInput.value = project.description || '';
            saveBtn.textContent = 'Update Project';
            modal.dataset.editIndex = editIndex;
        } else {
            title.textContent = 'Create New Project';
            nameInput.value = '';
            descInput.value = '';
            saveBtn.textContent = 'Save Project';
            delete modal.dataset.editIndex;
        }
        
        modal.style.display = 'flex';
        console.log("projects.js: Modal should now be visible");
        setTimeout(() => {
            if (nameInput) nameInput.focus();
        }, 100);
    }
    
    hideProjectModal() {
        const modal = document.getElementById('project-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }
    
    // Save project (create or edit)
    saveProject() {
        const modal = document.getElementById('project-modal');
        const nameInput = document.getElementById('project-name');
        const descInput = document.getElementById('project-description');
        
        const name = nameInput.value.trim();
        if (!name) {
            alert('Project name is required');
            nameInput.focus();
            return;
        }
        
        const project = {
            id: Date.now().toString(),
            name: name,
            description: descInput.value.trim(),
            systemInstructions: '',
            files: [],
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
        };
        
        const editIndex = modal.dataset.editIndex;
        if (editIndex !== undefined) {
            // Edit existing project
            const existing = this.projects[parseInt(editIndex)];
            project.id = existing.id;
            project.createdAt = existing.createdAt;
            project.files = existing.files || [];
            project.systemInstructions = existing.systemInstructions || '';
            this.projects[parseInt(editIndex)] = project;
        } else {
            // Create new project
            this.projects.push(project);
        }
        
        this.saveProjects();
        this.hideProjectModal();
        this.renderProjectsList();
    }
    
    // Edit project
    editProject(index) {
        this.showProjectModal(index);
    }
    
    
    // Delete project
    deleteProject(index) {
        if (index >= 0 && index < this.projects.length) {
            const project = this.projects[index];
            if (confirm(`Are you sure you want to delete "${project.name}"? This cannot be undone.`)) {
                this.projects.splice(index, 1);
                this.saveProjects();
                this.renderProjectsList();
                
                // If deleted project is currently open, go back to list
                if (this.currentProject && this.currentProject.id === project.id) {
                    this.showProjectsList();
                }
            }
        }
    }
    
    
    // Open project workspace
    openProject(index) {
        if (index >= 0 && index < this.projects.length) {
            this.currentProject = this.projects[index];
            this.currentProjectFiles = this.currentProject.files || [];
            this.showProjectWorkspace();
        }
    }
    
    // Show projects list view
    showProjectsList() {
        const listView = document.getElementById('projects-list-view');
        const workspaceView = document.getElementById('project-workspace-view');
        
        if (listView && workspaceView) {
            listView.style.display = 'block';
            workspaceView.classList.remove('active');
            this.isInWorkspace = false;
            this.currentProject = null;
            this.renderProjectsList();
        }
    }
    
    // Show project workspace view
    showProjectWorkspace() {
        const listView = document.getElementById('projects-list-view');
        const workspaceView = document.getElementById('project-workspace-view');
        
        if (listView && workspaceView && this.currentProject) {
            listView.style.display = 'none';
            workspaceView.classList.add('active');
            this.isInWorkspace = true;
            
            // Update workspace UI
            this.updateWorkspaceInfo();
            this.renderProjectFiles();
            this.initProjectChat();
        }
    }
    
    // Update workspace project info
    updateWorkspaceInfo() {
        const nameEl = document.getElementById('current-project-name');
        const descEl = document.getElementById('current-project-description');
        const contextEl = document.getElementById('project-context-indicator');
        const systemPromptEl = document.getElementById('system-prompt-display');
        
        if (nameEl && this.currentProject) {
            nameEl.textContent = this.currentProject.name;
        }
        
        if (descEl && this.currentProject) {
            descEl.textContent = this.currentProject.description || 'No description';
        }
        
        if (contextEl && this.currentProject) {
            const fileCount = this.currentProjectFiles.length;
            contextEl.textContent = `Context: Project + ${fileCount} file${fileCount !== 1 ? 's' : ''}`;
        }
        
        if (systemPromptEl && this.currentProject) {
            const instructions = this.currentProject.systemInstructions || '';
            if (instructions.trim()) {
                systemPromptEl.textContent = instructions;
                systemPromptEl.classList.remove('system-prompt-empty');
            } else {
                systemPromptEl.textContent = 'No system instructions set. Click Edit to add instructions.';
                systemPromptEl.classList.add('system-prompt-empty');
            }
        }
    }
    
    // Show system instructions modal
    showSystemInstructionsModal() {
        const modal = document.getElementById('system-instructions-modal');
        const input = document.getElementById('system-instructions-input');
        
        if (modal && input && this.currentProject) {
            input.value = this.currentProject.systemInstructions || '';
            modal.style.display = 'flex';
            setTimeout(() => input.focus(), 100);
        }
    }
    
    // Hide system instructions modal
    hideSystemInstructionsModal() {
        const modal = document.getElementById('system-instructions-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }
    
    // Save system instructions
    saveSystemInstructions() {
        const input = document.getElementById('system-instructions-input');
        
        if (input && this.currentProject) {
            this.currentProject.systemInstructions = input.value.trim();
            this.currentProject.updatedAt = new Date().toISOString();
            
            // Update in projects list
            const projectIndex = this.projects.findIndex(p => p.id === this.currentProject.id);
            if (projectIndex !== -1) {
                this.projects[projectIndex] = this.currentProject;
                this.saveProjects();
            }
            
            this.updateWorkspaceInfo();
            this.hideSystemInstructionsModal();
        }
    }
    
    // Handle file upload
    async handleFileUpload(files) {
        if (!this.currentProject) return;
        
        for (const file of files) {
            try {
                // Create file object
                const fileObj = {
                    id: Date.now().toString() + '_' + Math.random().toString(36).substr(2, 9),
                    name: file.name,
                    type: file.type,
                    size: file.size,
                    uploadedAt: new Date().toISOString()
                };
                
                // For demo purposes, we'll store file info only
                // In a real implementation, you'd upload to a server/cloud storage
                this.currentProjectFiles.push(fileObj);
                
                // Update project in the list
                this.currentProject.files = this.currentProjectFiles;
                const projectIndex = this.projects.findIndex(p => p.id === this.currentProject.id);
                if (projectIndex !== -1) {
                    this.projects[projectIndex] = this.currentProject;
                    this.saveProjects();
                }
                
                console.log(`File added: ${file.name}`);
            } catch (error) {
                console.error(`Error uploading file ${file.name}:`, error);
                alert(`Failed to upload ${file.name}. Please try again.`);
            }
        }
        
        // Clear the file input after successful upload
        const fileInput = document.getElementById('project-file-input');
        if (fileInput) {
            fileInput.value = '';
        }
        
        this.renderProjectFiles();
        this.updateWorkspaceInfo();
    }
    
    // Render project files list
    renderProjectFiles() {
        const container = document.getElementById('project-files-list');
        if (!container) return;
        
        if (this.currentProjectFiles.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-sm text-center">No files uploaded yet</p>';
            return;
        }
        
        container.innerHTML = '';
        
        this.currentProjectFiles.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'project-file-item';
            fileItem.innerHTML = `
                <div class="project-file-info">
                    <div class="project-file-name">${this.escapeHtml(file.name)}</div>
                    <div class="project-file-size">${this.formatFileSize(file.size)}</div>
                </div>
                <div class="project-file-actions">
                    <button class="file-delete-btn" data-index="${index}" title="Delete file">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            
            container.appendChild(fileItem);
            
            // Bind delete event
            fileItem.querySelector('.file-delete-btn').addEventListener('click', () => {
                this.deleteProjectFile(index);
            });
        });
    }
    
    // Delete project file
    deleteProjectFile(index) {
        if (index >= 0 && index < this.currentProjectFiles.length) {
            const file = this.currentProjectFiles[index];
            if (confirm(`Delete "${file.name}"?`)) {
                this.currentProjectFiles.splice(index, 1);
                
                // Update project
                this.currentProject.files = this.currentProjectFiles;
                const projectIndex = this.projects.findIndex(p => p.id === this.currentProject.id);
                if (projectIndex !== -1) {
                    this.projects[projectIndex] = this.currentProject;
                    this.saveProjects();
                }
                
                // Clear the file input to allow re-uploading the same file
                const fileInput = document.getElementById('project-file-input');
                if (fileInput) {
                    fileInput.value = '';
                }
                
                this.renderProjectFiles();
                this.updateWorkspaceInfo();
            }
        }
    }
    
    // Initialize project chat
    initProjectChat() {
        const messagesContainer = document.getElementById('project-chat-messages');
        if (messagesContainer && this.currentProject) {
            // Clear and add welcome message
            messagesContainer.innerHTML = `
                <div class="message message-system">
                    Welcome to ${this.escapeHtml(this.currentProject.name)}! I have access to your project context and ${this.currentProjectFiles.length} uploaded file${this.currentProjectFiles.length !== 1 ? 's' : ''}.
                </div>
            `;
        }
    }
    
    // Send project message
    sendProjectMessage() {
        const input = document.getElementById('project-chat-input');
        const messagesContainer = document.getElementById('project-chat-messages');
        
        if (!input || !messagesContainer || !this.currentProject) return;
        
        const text = input.value.trim();
        if (!text) return;
        
        // Add user message to chat
        const userMessage = document.createElement('div');
        userMessage.className = 'message message-user';
        userMessage.innerHTML = this.formatMessageContent(text);
        messagesContainer.appendChild(userMessage);
        
        // Clear input
        input.value = '';
        this.autoResizeTextarea.call(input);
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // TODO: Send to backend with project context
        // For now, add a demo response
        setTimeout(() => {
            const aiMessage = document.createElement('div');
            aiMessage.className = 'message message-ai';
            aiMessage.innerHTML = this.formatMessageContent(
                `I understand you're working on **${this.currentProject.name}**. I have access to your project files and context. How can I help you with this project?`
            );
            messagesContainer.appendChild(aiMessage);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }, 1000);
    }
    
    // Preview chat image
    previewChatImage(file) {
        const preview = document.getElementById('project-image-preview');
        const img = document.getElementById('project-preview-image');
        
        if (preview && img) {
            const reader = new FileReader();
            reader.onload = (e) => {
                img.src = e.target.result;
                preview.classList.remove('hidden');
            };
            reader.readAsDataURL(file);
        }
    }
    
    // Clear chat image preview
    clearChatImagePreview() {
        const preview = document.getElementById('project-image-preview');
        const fileInput = document.getElementById('project-file-input-chat');
        
        if (preview) preview.classList.add('hidden');
        if (fileInput) fileInput.value = '';
    }
    
    // Utility functions
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
    
    formatMessageContent(content) {
        if (!content) return '';
        try {
            return window.marked ? window.marked.parse(content) : content;
        } catch (e) {
            console.error("Markdown error:", e);
            return content;
        }
    }
    
    // Setup project workspace functionality
    setupProjectWorkspace() {
        // This method sets up the workspace-specific functionality
        console.log("Project workspace setup complete");
    }
}

// Initialize projects manager when DOM is ready
let projectsManager;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        projectsManager = new ProjectsManager();
        window.projectsManager = projectsManager;
    });
} else {
    projectsManager = new ProjectsManager();
    window.projectsManager = projectsManager;
}

// Make ProjectsManager available globally
window.ProjectsManager = ProjectsManager;