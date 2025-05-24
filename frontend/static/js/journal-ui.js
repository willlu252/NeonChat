// Journal UI Components and Controllers
class JournalUI {
    constructor() {
        this.currentEntry = null;
        this.entries = [];
        this.currentView = 'list'; // list, editor, viewer
        this.init();
    }

    init() {
        // Initialize with existing container
        this.ensureJournalStructure();
        this.bindEvents();
    }

    ensureJournalStructure() {
        const container = document.getElementById('journal-container');
        if (container && !container.querySelector('.journal-header')) {
            container.innerHTML = `
                <div class="journal-header">
                    <h2>My Journal</h2>
                    <div class="journal-actions">
                        <button id="new-entry-btn" class="btn btn-primary">
                            <i class="fas fa-plus"></i> New Entry
                        </button>
                        <button id="journal-stats-btn" class="btn btn-secondary">
                            <i class="fas fa-chart-line"></i> Stats
                        </button>
                    </div>
                </div>
                <div id="journal-content" class="journal-content">
                    <!-- Dynamic content goes here -->
                </div>
            `;
        }
    }

    bindEvents() {
        // New entry button
        document.getElementById('new-entry-btn')?.addEventListener('click', () => {
            this.showEditor();
        });

        // Stats button
        document.getElementById('journal-stats-btn')?.addEventListener('click', () => {
            this.showStats();
        });
    }

    // Show journal UI
    show() {
        document.getElementById('journal-container')?.classList.remove('hidden');
        document.getElementById('metrics-container')?.classList.add('hidden');
        this.loadEntries();
    }

    // Hide journal UI
    hide() {
        document.getElementById('journal-container')?.classList.add('hidden');
    }

    // Load journal entries
    async loadEntries() {
        try {
            const entries = await window.journalAPI.getEntries({ limit: 20 });
            this.entries = entries;
            this.showList();
        } catch (error) {
            console.error('Failed to load entries:', error);
            this.showError('Failed to load journal entries');
        }
    }

    // Show entries list
    showList() {
        this.currentView = 'list';
        const content = document.getElementById('journal-content');
        
        if (this.entries.length === 0) {
            content.innerHTML = `
                <div class="journal-empty">
                    <i class="fas fa-book fa-3x"></i>
                    <p>No journal entries yet</p>
                    <button class="btn btn-primary" onclick="journalUI.showEditor()">
                        Create Your First Entry
                    </button>
                </div>
            `;
            return;
        }

        const entriesHTML = this.entries.map(entry => `
            <div class="journal-entry-card" data-entry-id="${entry.id}">
                <div class="entry-header">
                    <h3>${entry.title || 'Untitled Entry'}</h3>
                    <span class="entry-date">${new Date(entry.entry_date).toLocaleDateString()}</span>
                </div>
                <div class="entry-preview">${this.truncateText(entry.content, 150)}</div>
                <div class="entry-meta">
                    ${entry.mood_score ? `<span class="mood-badge" data-mood="${entry.mood_score}">Mood: ${entry.mood_score}/10</span>` : ''}
                    ${entry.tags && entry.tags.length > 0 ? entry.tags.map(tag => `<span class="tag">${tag}</span>`).join('') : ''}
                </div>
                <div class="entry-actions">
                    <button class="btn btn-sm" onclick="journalUI.viewEntry('${entry.id}')">
                        <i class="fas fa-eye"></i> View
                    </button>
                    <button class="btn btn-sm" onclick="journalUI.editEntry('${entry.id}')">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="journalUI.deleteEntry('${entry.id}')">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        `).join('');

        content.innerHTML = `
            <div class="journal-filters">
                <input type="text" id="journal-search" placeholder="Search entries..." class="form-control">
                <input type="date" id="journal-date-filter" class="form-control">
                <select id="journal-mood-filter" class="form-control">
                    <option value="">All Moods</option>
                    <option value="1-3">Low (1-3)</option>
                    <option value="4-6">Medium (4-6)</option>
                    <option value="7-10">High (7-10)</option>
                </select>
            </div>
            <div class="journal-entries-list">
                ${entriesHTML}
            </div>
        `;

        // Bind filter events
        this.bindFilterEvents();
    }

    // Show journal editor
    showEditor(entryId = null) {
        this.currentView = 'editor';
        const content = document.getElementById('journal-content');
        const isEdit = !!entryId;
        
        let entry = { title: '', content: '', mood_score: null, energy_level: null };
        if (isEdit) {
            entry = this.entries.find(e => e.id === entryId) || entry;
        }

        content.innerHTML = `
            <div class="journal-editor-new">
                <div class="therapy-main-content">
                    <div class="therapy-view-container">
                        <div class="therapy-layout-flex">
                            <!-- Left side - Therapy Chat (using main chat structure) -->
                            <div class="therapy-chat-wrapper">
                                <div class="chat-canvas-revert therapy-canvas">
                                    <div id="therapy-messages" class="space-y-4">
                                        <div class="message message-ai">
                                            <div class="therapist-intro">
                                                <i class="fas fa-user-md"></i>
                                                <p>Hello! I'm here to listen and help you explore your thoughts and feelings. This is a safe space where you can share whatever is on your mind.</p>
                                                <p>How are you feeling today?</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="chat-hud-revert">
                                    <div class="chat-hud-container">
                                        <div id="therapy-image-preview" class="image-preview hidden">
                                            <img id="therapy-preview-image" src="" alt="Image preview">
                                            <div class="image-preview-controls mt-2">
                                                <button class="clear-image" onclick="journalUI.clearTherapyImage()">Remove</button>
                                            </div>
                                        </div>
                                        <div class="input-area">
                                            <div class="input-buttons">
                                                <label for="therapy-file-input" class="attachment-btn">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                                        <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path>
                                                    </svg>
                                                </label>
                                                <input type="file" id="therapy-file-input" accept="image/*" hidden>
                                            </div>
                                            <textarea id="therapy-input" class="chat-input" rows="1" placeholder="Share what's on your mind..."></textarea>
                                            <button id="send-therapy-message" class="send-btn">Send</button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Right side - Metrics (using similar structure) -->
                            <div class="metrics-wrapper">
                                <div class="metrics-canvas">
                                    <div class="metrics-header-section">
                                        <h3 class="metrics-header">How are you feeling?</h3>
                                    </div>
                                    <div class="metrics-scroll-content">
                            <!-- Physical Health -->
                            <div class="metric-section">
                                <h5><i class="fas fa-heart"></i> Physical Health</h5>
                                
                                <div class="metric-item">
                                    <label>Overall Health</label>
                                    <div class="metric-controls">
                                        <input type="range" id="physical-health" min="1" max="10" value="5">
                                        <input type="number" id="physical-health-number" min="1" max="10" value="5" class="metric-number">
                                        <div class="metric-spinner">
                                            <button type="button" class="metric-spin-up" data-target="physical-health">▲</button>
                                            <button type="button" class="metric-spin-down" data-target="physical-health">▼</button>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="metric-item">
                                    <label>Sleep Quality</label>
                                    <div class="metric-controls">
                                        <input type="range" id="sleep-quality" min="1" max="10" value="5">
                                        <input type="number" id="sleep-quality-number" min="1" max="10" value="5" class="metric-number">
                                        <div class="metric-spinner">
                                            <button type="button" class="metric-spin-up" data-target="sleep-quality">▲</button>
                                            <button type="button" class="metric-spin-down" data-target="sleep-quality">▼</button>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="metric-item">
                                    <label>Energy Level</label>
                                    <div class="metric-controls">
                                        <input type="range" id="energy-level" min="1" max="10" value="5">
                                        <input type="number" id="energy-level-number" min="1" max="10" value="5" class="metric-number">
                                        <div class="metric-spinner">
                                            <button type="button" class="metric-spin-up" data-target="energy-level">▲</button>
                                            <button type="button" class="metric-spin-down" data-target="energy-level">▼</button>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="metric-item">
                                    <label>Diet Quality</label>
                                    <div class="metric-controls">
                                        <input type="range" id="diet-quality" min="1" max="10" value="5">
                                        <input type="number" id="diet-quality-number" min="1" max="10" value="5" class="metric-number">
                                        <div class="metric-spinner">
                                            <button type="button" class="metric-spin-up" data-target="diet-quality">▲</button>
                                            <button type="button" class="metric-spin-down" data-target="diet-quality">▼</button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Mental & Emotional -->
                            <div class="metric-section">
                                <h5><i class="fas fa-brain"></i> Mental & Emotional</h5>
                                
                                <div class="metric-item">
                                    <label>Mood</label>
                                    <div class="metric-controls">
                                        <input type="range" id="mood-score" min="1" max="10" value="5">
                                        <input type="number" id="mood-score-number" min="1" max="10" value="5" class="metric-number">
                                        <div class="metric-spinner">
                                            <button type="button" class="metric-spin-up" data-target="mood-score">▲</button>
                                            <button type="button" class="metric-spin-down" data-target="mood-score">▼</button>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="metric-item">
                                    <label>Stress Level</label>
                                    <div class="metric-controls">
                                        <input type="range" id="stress-level" min="1" max="10" value="5">
                                        <input type="number" id="stress-level-number" min="1" max="10" value="5" class="metric-number">
                                        <div class="metric-spinner">
                                            <button type="button" class="metric-spin-up" data-target="stress-level">▲</button>
                                            <button type="button" class="metric-spin-down" data-target="stress-level">▼</button>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="metric-item">
                                    <label>Anxiety Level</label>
                                    <div class="metric-controls">
                                        <input type="range" id="anxiety-level" min="1" max="10" value="5">
                                        <input type="number" id="anxiety-level-number" min="1" max="10" value="5" class="metric-number">
                                        <div class="metric-spinner">
                                            <button type="button" class="metric-spin-up" data-target="anxiety-level">▲</button>
                                            <button type="button" class="metric-spin-down" data-target="anxiety-level">▼</button>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="metric-item">
                                    <label>Happiness</label>
                                    <div class="metric-controls">
                                        <input type="range" id="happiness-level" min="1" max="10" value="5">
                                        <input type="number" id="happiness-level-number" min="1" max="10" value="5" class="metric-number">
                                        <div class="metric-spinner">
                                            <button type="button" class="metric-spin-up" data-target="happiness-level">▲</button>
                                            <button type="button" class="metric-spin-down" data-target="happiness-level">▼</button>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="metric-item">
                                    <label>Clarity of Mind</label>
                                    <div class="metric-controls">
                                        <input type="range" id="clarity-level" min="1" max="10" value="5">
                                        <input type="number" id="clarity-level-number" min="1" max="10" value="5" class="metric-number">
                                        <div class="metric-spinner">
                                            <button type="button" class="metric-spin-up" data-target="clarity-level">▲</button>
                                            <button type="button" class="metric-spin-down" data-target="clarity-level">▼</button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Relationships -->
                            <div class="metric-section">
                                <h5><i class="fas fa-users"></i> Relationships</h5>
                                
                                <div class="metric-item">
                                    <label>Family Relations</label>
                                    <div class="metric-controls">
                                        <input type="range" id="family-relations" min="1" max="10" value="5">
                                        <input type="number" id="family-relations-number" min="1" max="10" value="5" class="metric-number">
                                        <div class="metric-spinner">
                                            <button type="button" class="metric-spin-up" data-target="family-relations">▲</button>
                                            <button type="button" class="metric-spin-down" data-target="family-relations">▼</button>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="metric-item">
                                    <label>Friendships</label>
                                    <div class="metric-controls">
                                        <input type="range" id="friendships" min="1" max="10" value="5">
                                        <input type="number" id="friendships-number" min="1" max="10" value="5" class="metric-number">
                                        <div class="metric-spinner">
                                            <button type="button" class="metric-spin-up" data-target="friendships">▲</button>
                                            <button type="button" class="metric-spin-down" data-target="friendships">▼</button>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="metric-item">
                                    <label>Romantic Life</label>
                                    <div class="metric-controls">
                                        <input type="range" id="romantic-life" min="1" max="10" value="5">
                                        <input type="number" id="romantic-life-number" min="1" max="10" value="5" class="metric-number">
                                        <div class="metric-spinner">
                                            <button type="button" class="metric-spin-up" data-target="romantic-life">▲</button>
                                            <button type="button" class="metric-spin-down" data-target="romantic-life">▼</button>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="metric-item">
                                    <label>Social Satisfaction</label>
                                    <div class="metric-controls">
                                        <input type="range" id="social-satisfaction" min="1" max="10" value="5">
                                        <input type="number" id="social-satisfaction-number" min="1" max="10" value="5" class="metric-number">
                                        <div class="metric-spinner">
                                            <button type="button" class="metric-spin-up" data-target="social-satisfaction">▲</button>
                                            <button type="button" class="metric-spin-down" data-target="social-satisfaction">▼</button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Work & Productivity -->
                            <div class="metric-section">
                                <h5><i class="fas fa-briefcase"></i> Work & Career</h5>
                                
                                <div class="metric-item">
                                    <label>Work Satisfaction</label>
                                    <div class="metric-controls">
                                        <input type="range" id="work-satisfaction" min="1" max="10" value="5">
                                        <input type="number" id="work-satisfaction-number" min="1" max="10" value="5" class="metric-number">
                                        <div class="metric-spinner">
                                            <button type="button" class="metric-spin-up" data-target="work-satisfaction">▲</button>
                                            <button type="button" class="metric-spin-down" data-target="work-satisfaction">▼</button>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="metric-item">
                                    <label>Productivity</label>
                                    <div class="metric-controls">
                                        <input type="range" id="productivity" min="1" max="10" value="5">
                                        <input type="number" id="productivity-number" min="1" max="10" value="5" class="metric-number">
                                        <div class="metric-spinner">
                                            <button type="button" class="metric-spin-up" data-target="productivity">▲</button>
                                            <button type="button" class="metric-spin-down" data-target="productivity">▼</button>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="metric-item">
                                    <label>Work-Life Balance</label>
                                    <div class="metric-controls">
                                        <input type="range" id="work-life-balance" min="1" max="10" value="5">
                                        <input type="number" id="work-life-balance-number" min="1" max="10" value="5" class="metric-number">
                                        <div class="metric-spinner">
                                            <button type="button" class="metric-spin-up" data-target="work-life-balance">▲</button>
                                            <button type="button" class="metric-spin-down" data-target="work-life-balance">▼</button>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="metric-item">
                                    <label>Career Progress</label>
                                    <div class="metric-controls">
                                        <input type="range" id="career-progress" min="1" max="10" value="5">
                                        <input type="number" id="career-progress-number" min="1" max="10" value="5" class="metric-number">
                                        <div class="metric-spinner">
                                            <button type="button" class="metric-spin-up" data-target="career-progress">▲</button>
                                            <button type="button" class="metric-spin-down" data-target="career-progress">▼</button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Spiritual & Personal Growth -->
                            <div class="metric-section">
                                <h5><i class="fas fa-om"></i> Spiritual & Growth</h5>
                                
                                <div class="metric-item">
                                    <label>Spiritual Connection</label>
                                    <div class="metric-controls">
                                        <input type="range" id="spiritual-connection" min="1" max="10" value="5">
                                        <input type="number" id="spiritual-connection-number" min="1" max="10" value="5" class="metric-number">
                                        <div class="metric-spinner">
                                            <button type="button" class="metric-spin-up" data-target="spiritual-connection">▲</button>
                                            <button type="button" class="metric-spin-down" data-target="spiritual-connection">▼</button>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="metric-item">
                                    <label>Personal Growth</label>
                                    <div class="metric-controls">
                                        <input type="range" id="personal-growth" min="1" max="10" value="5">
                                        <input type="number" id="personal-growth-number" min="1" max="10" value="5" class="metric-number">
                                        <div class="metric-spinner">
                                            <button type="button" class="metric-spin-up" data-target="personal-growth">▲</button>
                                            <button type="button" class="metric-spin-down" data-target="personal-growth">▼</button>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="metric-item">
                                    <label>Life Purpose</label>
                                    <div class="metric-controls">
                                        <input type="range" id="life-purpose" min="1" max="10" value="5">
                                        <input type="number" id="life-purpose-number" min="1" max="10" value="5" class="metric-number">
                                        <div class="metric-spinner">
                                            <button type="button" class="metric-spin-up" data-target="life-purpose">▲</button>
                                            <button type="button" class="metric-spin-down" data-target="life-purpose">▼</button>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="metric-item">
                                    <label>Inner Peace</label>
                                    <div class="metric-controls">
                                        <input type="range" id="inner-peace" min="1" max="10" value="5">
                                        <input type="number" id="inner-peace-number" min="1" max="10" value="5" class="metric-number">
                                        <div class="metric-spinner">
                                            <button type="button" class="metric-spin-up" data-target="inner-peace">▲</button>
                                            <button type="button" class="metric-spin-down" data-target="inner-peace">▼</button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Activities -->
                            <div class="metric-section">
                                <h5><i class="fas fa-check-square"></i> Today's Activities</h5>
                                
                                <div class="toggle-item">
                                    <label>
                                        <input type="checkbox" id="exercised"> Exercised
                                    </label>
                                </div>
                                
                                <div class="toggle-item">
                                    <label>
                                        <input type="checkbox" id="meditated"> Meditated
                                    </label>
                                </div>
                                
                                <div class="toggle-item">
                                    <label>
                                        <input type="checkbox" id="journaled"> Journaled
                                    </label>
                                </div>
                                
                                <div class="toggle-item">
                                    <label>
                                        <input type="checkbox" id="social-time"> Social Time
                                    </label>
                                </div>
                                
                                <div class="toggle-item">
                                    <label>
                                        <input type="checkbox" id="creative-time"> Creative Time
                                    </label>
                                </div>
                                
                                <div class="toggle-item">
                                    <label>
                                        <input type="checkbox" id="outdoor-time"> Outdoor Time
                                    </label>
                                </div>
                            </div>
                            
                            <div class="save-session-btn">
                                <button type="button" class="btn btn-primary btn-block" onclick="journalUI.saveTherapySession()">
                                    <i class="fas fa-save"></i> Save Session
                                </button>
                            </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Set current entry for editing
        if (isEdit) {
            this.currentEntry = entry;
            // Load existing content into chat if editing
            if (entry.content) {
                this.loadExistingChat(entry.content);
            }
        }

        // Initialize therapy chat
        this.initTherapyChat();
        this.bindEditorEvents();
    }

    // View journal entry
    async viewEntry(entryId) {
        try {
            const entry = await window.journalAPI.getEntry(entryId);
            this.showViewer(entry);
        } catch (error) {
            console.error('Failed to load entry:', error);
            this.showError('Failed to load entry');
        }
    }

    // Show entry viewer
    showViewer(entry) {
        this.currentView = 'viewer';
        const content = document.getElementById('journal-content');
        
        content.innerHTML = `
            <div class="journal-viewer">
                <div class="viewer-header">
                    <button class="btn btn-secondary" onclick="journalUI.showList()">
                        <i class="fas fa-arrow-left"></i> Back
                    </button>
                    <div class="viewer-actions">
                        <button class="btn btn-primary" onclick="journalUI.editEntry('${entry.id}')">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                        <button class="btn btn-danger" onclick="journalUI.deleteEntry('${entry.id}')">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                </div>
                
                <article class="journal-article">
                    <header>
                        <h1>${entry.title || 'Untitled Entry'}</h1>
                        <div class="article-meta">
                            <time>${new Date(entry.created_at).toLocaleString()}</time>
                            <span class="word-count">${entry.word_count} words</span>
                        </div>
                    </header>
                    
                    <div class="article-content">
                        ${this.formatContent(entry.content)}
                    </div>
                    
                    <footer class="article-footer">
                        ${entry.mood_score ? `
                            <div class="mood-display">
                                <i class="fas fa-smile"></i>
                                Mood: ${entry.mood_score}/10
                            </div>
                        ` : ''}
                        ${entry.energy_level ? `
                            <div class="energy-display">
                                <i class="fas fa-battery-half"></i>
                                Energy: ${entry.energy_level}/10
                            </div>
                        ` : ''}
                        ${entry.tags && entry.tags.length > 0 ? `
                            <div class="tags-display">
                                ${entry.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                            </div>
                        ` : ''}
                        ${entry.ai_observations ? `
                            <div class="ai-observations">
                                <h4>AI Observations</h4>
                                <p>${entry.ai_observations}</p>
                            </div>
                        ` : ''}
                    </footer>
                </article>
            </div>
        `;
    }

    // Edit entry
    editEntry(entryId) {
        this.showEditor(entryId);
    }

    // Delete entry
    async deleteEntry(entryId) {
        if (!confirm('Are you sure you want to delete this entry?')) return;
        
        try {
            await window.journalAPI.deleteEntry(entryId);
            this.loadEntries();
        } catch (error) {
            console.error('Failed to delete entry:', error);
            this.showError('Failed to delete entry');
        }
    }

    // Initialize therapy chat
    initTherapyChat() {
        this.therapyMessages = [];
        this.therapyConversation = '';
        this.currentTherapyImage = null;
        
        // Bind therapy chat events
        const therapyInput = document.getElementById('therapy-input');
        const sendButton = document.getElementById('send-therapy-message');
        const fileInput = document.getElementById('therapy-file-input');
        
        if (therapyInput) {
            therapyInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendTherapyMessage();
                }
            });
            
            // Handle pasted images
            therapyInput.addEventListener('paste', (e) => {
                const items = (e.clipboardData || e.originalEvent.clipboardData).items;
                for (const item of items) {
                    if (item.type.indexOf('image') === 0) {
                        const blob = item.getAsFile();
                        this.handleTherapyImage(blob);
                        e.preventDefault();
                        break;
                    }
                }
            });
        }
        
        if (sendButton) {
            sendButton.addEventListener('click', () => this.sendTherapyMessage());
        }
        
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file && file.type.startsWith('image/')) {
                    this.handleTherapyImage(file);
                }
            });
        }
    }
    
    // Handle therapy image
    handleTherapyImage(file) {
        this.currentTherapyImage = file;
        
        const reader = new FileReader();
        reader.onload = (event) => {
            document.getElementById('therapy-preview-image').src = event.target.result;
            document.getElementById('therapy-image-preview').classList.remove('hidden');
        };
        reader.readAsDataURL(file);
    }
    
    // Clear therapy image
    clearTherapyImage() {
        this.currentTherapyImage = null;
        document.getElementById('therapy-image-preview').classList.add('hidden');
        document.getElementById('therapy-file-input').value = '';
    }
    
    // Send therapy message
    async sendTherapyMessage() {
        const input = document.getElementById('therapy-input');
        const messagesContainer = document.getElementById('therapy-messages');
        
        if (!input || (!input.value.trim() && !this.currentTherapyImage)) return;
        
        const userMessage = input.value.trim();
        input.value = '';
        
        // Create message object
        const messageData = {
            role: 'user',
            content: userMessage,
            timestamp: new Date().toISOString()
        };
        
        // Add user message to chat
        const userMsgDiv = document.createElement('div');
        userMsgDiv.className = 'message message-user';
        
        let messageHTML = '';
        
        // Add image if present
        if (this.currentTherapyImage) {
            const imageUrl = URL.createObjectURL(this.currentTherapyImage);
            messageHTML += `<img src="${imageUrl}" alt="Shared image" class="message-image" style="max-width: 300px; border-radius: 8px; margin-bottom: 0.5rem;">`;
            messageData.image = await this.imageToBase64(this.currentTherapyImage);
            messageData.imageName = this.currentTherapyImage.name;
        }
        
        if (userMessage) {
            messageHTML += `<p>${this.escapeHtml(userMessage)}</p>`;
        }
        
        userMsgDiv.innerHTML = messageHTML;
        messagesContainer.appendChild(userMsgDiv);
        
        // Clear image preview
        if (this.currentTherapyImage) {
            this.clearTherapyImage();
        }
        
        // Add to conversation
        this.therapyMessages.push(messageData);
        
        // Show typing indicator
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message message-ai typing-indicator-therapy';
        typingDiv.innerHTML = `
            <div class="typing-dots">
                <span></span><span></span><span></span>
            </div>
        `;
        messagesContainer.appendChild(typingDiv);
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        try {
            // Get current metrics for context
            const metrics = this.getCurrentMetrics();
            
            // Send to Claude API with therapy prompt
            const response = await this.callTherapistClaude(userMessage, metrics);
            
            // Remove typing indicator
            typingDiv.remove();
            
            // Add AI response
            const aiMsgDiv = document.createElement('div');
            aiMsgDiv.className = 'message message-ai';
            aiMsgDiv.innerHTML = `<p>${this.formatResponse(response)}</p>`;
            messagesContainer.appendChild(aiMsgDiv);
            
            // Add to conversation
            this.therapyMessages.push({ role: 'assistant', content: response });
            
            // Scroll to bottom
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
            
        } catch (error) {
            console.error('Therapy chat error:', error);
            typingDiv.remove();
            
            // Show error message
            const errorDiv = document.createElement('div');
            errorDiv.className = 'message message-system';
            errorDiv.innerHTML = `<p>I'm having trouble connecting right now. Please try again.</p>`;
            messagesContainer.appendChild(errorDiv);
        }
    }
    
    // Call Claude API with therapist personality
    async callTherapistClaude(message, metrics) {
        // For now, return a mock response since backend is not connected
        // In production, this would call the actual Claude API
        const responses = [
            "Thank you for sharing that with me. It sounds like you're experiencing some complex feelings. Can you tell me more about what's been on your mind lately?",
            "I hear you, and I appreciate your openness. How long have you been feeling this way?",
            "That's a significant insight. What do you think might be contributing to these feelings?",
            "It takes courage to share these thoughts. How are these feelings affecting your daily life?",
            "I understand. Let's explore this together. What would you like to see change in your situation?"
        ];
        
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000));
        
        return responses[Math.floor(Math.random() * responses.length)];
    }
    
    // Get current metrics
    getCurrentMetrics() {
        const metrics = {};
        
        // Collect all range inputs
        document.querySelectorAll('.metrics-sidebar input[type="range"]').forEach(input => {
            metrics[input.id] = parseInt(input.value);
        });
        
        // Collect all checkboxes
        document.querySelectorAll('.metrics-sidebar input[type="checkbox"]').forEach(input => {
            metrics[input.id] = input.checked;
        });
        
        return metrics;
    }
    
    // Save therapy session
    async saveTherapySession() {
        // Auto-generate title with date and time
        const now = new Date();
        const title = `Diary Entry ${now.toLocaleDateString()} ${now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`;
        const metrics = this.getCurrentMetrics();
        
        // Format conversation for storage, including images
        const content = this.therapyMessages.map(msg => {
            let messageContent = `**${msg.role === 'user' ? 'You' : 'Therapist'}:** `;
            
            // Add image if present
            if (msg.image) {
                messageContent += `\n![${msg.imageName || 'Image'}](${msg.image})\n`;
            }
            
            // Add text content
            if (msg.content) {
                messageContent += msg.content;
            }
            
            return messageContent;
        }).join('\n\n');
        
        // Extract all images from the conversation
        const images = this.therapyMessages
            .filter(msg => msg.image)
            .map(msg => ({
                data: msg.image,
                name: msg.imageName || 'image.png',
                timestamp: msg.timestamp
            }));
        
        const entryData = {
            title,
            content,
            mood_score: metrics['mood-score'],
            energy_level: metrics['energy-level'],
            metrics: metrics,
            type: 'therapy_session',
            therapist_notes: this.generateTherapistNotes(metrics),
            images: images  // Include images in the saved data
        };
        
        try {
            let result;
            if (this.currentEntry && this.currentEntry.id) {
                // Update existing entry
                result = await window.journalAPI.updateEntry(this.currentEntry.id, entryData);
            } else {
                // Create new entry
                result = await window.journalAPI.createEntry(entryData);
            }
            
            // Show success message
            this.showMessage('Session saved successfully!', 'success');
            
            // Return to list after a delay
            setTimeout(() => {
                this.loadEntries();
                this.showList();
            }, 1500);
            
        } catch (error) {
            console.error('Failed to save session:', error);
            this.showMessage('Failed to save session. Please try again.', 'error');
        }
    }
    
    // Generate therapist notes based on metrics
    generateTherapistNotes(metrics) {
        const notes = [];
        
        // Analyze key metrics
        if (metrics['mood-score'] < 4) {
            notes.push('Low mood observed. May benefit from mood-lifting activities.');
        }
        if (metrics['stress-level'] > 7) {
            notes.push('High stress levels reported. Consider stress management techniques.');
        }
        if (metrics['sleep-quality'] < 5) {
            notes.push('Poor sleep quality. Sleep hygiene improvements recommended.');
        }
        
        return notes.join(' ');
    }
    
    // Show message
    showMessage(message, type = 'info') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `therapy-message-toast ${type}`;
        messageDiv.innerHTML = message;
        document.body.appendChild(messageDiv);
        
        setTimeout(() => messageDiv.remove(), 3000);
    }
    
    // Bind editor events
    bindEditorEvents() {
        // Bind all range inputs to update their display values and sync with number inputs
        document.querySelectorAll('.metrics-scroll-content input[type="range"]').forEach(input => {
            const numberId = input.id + '-number';
            const numberInput = document.getElementById(numberId);
            
            const updateFromSlider = () => {
                // Update the value span if it exists (for old format)
                const valueSpan = input.parentElement.querySelector('.metric-value');
                if (valueSpan) {
                    valueSpan.textContent = input.value;
                }
                
                // Update the number input if it exists (for new format)
                if (numberInput) {
                    numberInput.value = input.value;
                }
            };
            
            const updateFromNumber = () => {
                if (numberInput) {
                    input.value = numberInput.value;
                    // Update value span if it exists
                    const valueSpan = input.parentElement.querySelector('.metric-value');
                    if (valueSpan) {
                        valueSpan.textContent = numberInput.value;
                    }
                }
            };
            
            // Bind slider events
            input.addEventListener('input', updateFromSlider);
            updateFromSlider(); // Set initial value
            
            // Bind number input events if it exists
            if (numberInput) {
                numberInput.addEventListener('input', updateFromNumber);
                numberInput.addEventListener('change', updateFromNumber);
            }
        });
        
        // Also bind all number inputs that might not have been caught above
        document.querySelectorAll('.metric-number').forEach(numberInput => {
            const sliderId = numberInput.id.replace('-number', '');
            const sliderInput = document.getElementById(sliderId);
            
            if (sliderInput) {
                const updateFromNumber = () => {
                    sliderInput.value = numberInput.value;
                    // Update value span if it exists
                    const valueSpan = sliderInput.parentElement.querySelector('.metric-value');
                    if (valueSpan) {
                        valueSpan.textContent = numberInput.value;
                    }
                };
                
                numberInput.addEventListener('input', updateFromNumber);
                numberInput.addEventListener('change', updateFromNumber);
            }
        });
        
        // Bind custom spinner buttons
        document.querySelectorAll('.metric-spin-up, .metric-spin-down').forEach(button => {
            button.addEventListener('click', (e) => {
                const targetId = e.target.dataset.target;
                const numberInput = document.getElementById(targetId + '-number');
                const sliderInput = document.getElementById(targetId);
                
                if (numberInput && sliderInput) {
                    let currentValue = parseInt(numberInput.value);
                    const isUp = e.target.classList.contains('metric-spin-up');
                    
                    if (isUp && currentValue < 10) {
                        currentValue++;
                    } else if (!isUp && currentValue > 1) {
                        currentValue--;
                    }
                    
                    // Update both inputs
                    numberInput.value = currentValue;
                    sliderInput.value = currentValue;
                    
                    // Trigger events to update any dependent elements
                    numberInput.dispatchEvent(new Event('input'));
                    sliderInput.dispatchEvent(new Event('input'));
                }
            });
        });
    }
    
    // Utility functions
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    formatResponse(text) {
        // Convert markdown to HTML if marked is available
        if (window.marked) {
            return marked.parse(text);
        }
        return this.escapeHtml(text);
    }
    
    // Convert image to base64
    async imageToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => resolve(reader.result);
            reader.onerror = error => reject(error);
        });
    }

    // Save journal entry
    async saveEntry() {
        const title = document.getElementById('entry-title').value;
        const content = document.getElementById('entry-content').value;
        const moodScore = parseInt(document.getElementById('mood-score').value);
        const energyLevel = parseInt(document.getElementById('energy-level').value);

        if (!content.trim()) {
            alert('Please write something in your journal entry');
            return;
        }

        const entryData = {
            title,
            content,
            mood_score: moodScore,
            energy_level: energyLevel
        };

        try {
            let result;
            if (this.currentEntry && this.currentEntry.id) {
                // Update existing entry
                result = await window.journalAPI.updateEntry(this.currentEntry.id, entryData);
            } else {
                // Create new entry
                result = await window.journalAPI.createEntry(entryData);
            }

            // Auto-analyze after saving
            if (result.id) {
                this.autoAnalyze(result.id, content, moodScore);
            }

            this.loadEntries();
            this.showList();
        } catch (error) {
            console.error('Failed to save entry:', error);
            this.showError('Failed to save entry');
        }
    }

    // Auto-analyze entry
    async autoAnalyze(entryId, content, moodScore) {
        try {
            // Generate tags
            const tags = await window.journalAPI.generateTags(content);
            
            // Get AI insights
            const insights = await window.journalAPI.getAIInsights(content, moodScore);
            
            // Update entry with analysis results
            if (tags.length > 0 || insights) {
                await window.journalAPI.updateEntry(entryId, {
                    tags: tags,
                    ai_observations: insights
                });
            }
        } catch (error) {
            console.error('Auto-analyze failed:', error);
            // Don't show error to user - this is a background operation
        }
    }

    // Analyze current entry
    async analyzeEntry() {
        const content = document.getElementById('entry-content').value;
        const moodScore = parseInt(document.getElementById('mood-score').value);
        
        if (!content.trim()) {
            alert('Please write something to analyze');
            return;
        }

        try {
            // Show loading
            const insightsContainer = document.getElementById('ai-insights-container');
            const insightsDiv = document.getElementById('ai-insights');
            insightsContainer.style.display = 'block';
            insightsDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';

            // Get analysis
            const [moodAnalysis, tags, insights] = await Promise.all([
                window.journalAPI.analyzeEntry(content, moodScore),
                window.journalAPI.generateTags(content),
                window.journalAPI.getAIInsights(content, moodScore)
            ]);

            // Display results
            let resultsHTML = '';
            
            if (moodAnalysis) {
                resultsHTML += `
                    <div class="analysis-section">
                        <h5>Mood Analysis</h5>
                        <p>Detected mood: ${moodAnalysis.sentiment} (confidence: ${Math.round(moodAnalysis.confidence * 100)}%)</p>
                        ${moodAnalysis.dominant_emotion ? `<p>Primary emotion: ${moodAnalysis.dominant_emotion}</p>` : ''}
                    </div>
                `;
            }
            
            if (tags && tags.length > 0) {
                resultsHTML += `
                    <div class="analysis-section">
                        <h5>Suggested Tags</h5>
                        <div>${tags.map(tag => `<span class="tag">${tag}</span>`).join('')}</div>
                    </div>
                `;
            }
            
            if (insights) {
                resultsHTML += `
                    <div class="analysis-section">
                        <h5>AI Insights</h5>
                        <p>${insights}</p>
                    </div>
                `;
            }

            insightsDiv.innerHTML = resultsHTML || '<p>No insights available</p>';
        } catch (error) {
            console.error('Analysis failed:', error);
            document.getElementById('ai-insights').innerHTML = '<p class="text-danger">Analysis failed</p>';
        }
    }

    // Get journal prompt
    async getPrompt() {
        const moodScore = parseInt(document.getElementById('mood-score').value);
        
        try {
            const prompts = await window.journalAPI.getJournalPrompts(moodScore);
            
            if (prompts && prompts.length > 0) {
                const prompt = prompts[Math.floor(Math.random() * prompts.length)];
                const content = document.getElementById('entry-content');
                
                if (content.value.trim()) {
                    content.value += '\n\n' + prompt;
                } else {
                    content.value = prompt;
                }
                
                this.updateWordCount();
            }
        } catch (error) {
            console.error('Failed to get prompt:', error);
        }
    }

    // Show statistics
    async showStats() {
        try {
            const stats = await window.journalAPI.getStats();
            const trends = await window.metricsAPI.getWeeklyTrends(4);
            
            const content = document.getElementById('journal-content');
            content.innerHTML = `
                <div class="journal-stats">
                    <div class="stats-header">
                        <button class="btn btn-secondary" onclick="journalUI.showList()">
                            <i class="fas fa-arrow-left"></i> Back
                        </button>
                        <h3>Journal Statistics</h3>
                    </div>
                    
                    <div class="stats-grid">
                        <div class="stat-card">
                            <i class="fas fa-book"></i>
                            <h4>${stats.total_entries}</h4>
                            <p>Total Entries</p>
                        </div>
                        
                        <div class="stat-card">
                            <i class="fas fa-pen"></i>
                            <h4>${stats.total_words}</h4>
                            <p>Total Words</p>
                        </div>
                        
                        <div class="stat-card">
                            <i class="fas fa-smile"></i>
                            <h4>${stats.avg_mood || 'N/A'}</h4>
                            <p>Average Mood</p>
                        </div>
                        
                        <div class="stat-card">
                            <i class="fas fa-battery-half"></i>
                            <h4>${stats.avg_energy || 'N/A'}</h4>
                            <p>Average Energy</p>
                        </div>
                    </div>
                    
                    <div class="chart-container">
                        <canvas id="mood-chart"></canvas>
                    </div>
                </div>
            `;
            
            // Draw mood chart if data available
            if (stats.entries_by_date && Object.keys(stats.entries_by_date).length > 0) {
                this.drawMoodChart(stats.entries_by_date);
            }
        } catch (error) {
            console.error('Failed to load stats:', error);
            this.showError('Failed to load statistics');
        }
    }

    // Helper methods
    updateWordCount() {
        const content = document.getElementById('entry-content')?.value || '';
        const wordCount = content.trim().split(/\s+/).filter(word => word.length > 0).length;
        const wordCountElement = document.getElementById('word-count');
        if (wordCountElement) {
            wordCountElement.textContent = `${wordCount} words`;
        }
    }

    truncateText(text, maxLength) {
        if (!text || text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    formatContent(content) {
        // Convert markdown to HTML if marked is available
        if (window.marked) {
            return marked.parse(content);
        }
        // Otherwise, preserve line breaks
        return content.replace(/\n/g, '<br>');
    }

    showError(message) {
        const content = document.getElementById('journal-content');
        content.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle"></i> ${message}
            </div>
        `;
    }

    bindFilterEvents() {
        // Implement filtering logic here
    }

    drawMoodChart(entriesByDate) {
        // Implement chart drawing if Chart.js is available
    }
}

// Create global instance
window.journalUI = new JournalUI();