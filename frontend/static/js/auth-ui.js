// Helper function to get backend URL
function getBackendUrl() {
    return window.location.hostname === 'localhost' 
        ? 'http://localhost:8000'  // Backend URL in development
        : window.location.origin;   // Same origin in production
}

// Authentication UI Components
class AuthUI {
    constructor() {
        this.init();
    }

    init() {
        // Check if backend has authentication enabled
        this.checkAuthStatus();
        this.bindEvents();
    }

    async checkAuthStatus() {
        try {
            // Try to verify if auth is available
            const response = await fetch(getBackendUrl() + '/api/auth/verify-token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('Auth status:', data);
                
                // Auth routes are available
                if (window.authService.isAuthenticated()) {
                    this.showAuthenticatedUI();
                } else {
                    this.showLoginForm();
                }
            } else if (response.status === 404) {
                // Auth routes not available - show demo mode
                this.showDemoMode();
            } else {
                // Auth available but not authenticated
                this.showLoginForm();
            }
        } catch (error) {
            console.error('Auth check error:', error);
            // If we can't reach the backend, show demo mode
            this.showDemoMode();
        }
    }

    showDemoMode() {
        // Hide auth container if it exists
        document.getElementById('auth-container')?.remove();
        document.querySelector('.main-content-revert').style.display = '';
        
        // Show demo mode in user section
        const userSection = document.getElementById('user-section');
        if (userSection) {
            userSection.style.display = 'block';
            userSection.innerHTML = `
                <div class="demo-mode-notice">
                    <i class="fas fa-info-circle"></i>
                    <p>Demo Mode</p>
                    <small>Authentication not configured</small>
                </div>
            `;
        }
        
        // Disable journal and metrics nav
        document.getElementById('journal-nav')?.classList.add('disabled');
        document.getElementById('metrics-nav')?.classList.add('disabled');
    }

    bindEvents() {
        // Logout button
        document.getElementById('logout-btn')?.addEventListener('click', () => {
            window.authService.logout();
        });
    }

    showLoginForm() {
        // Hide main content and show login
        document.querySelector('.main-content-revert').style.display = 'none';
        
        // Create login container if it doesn't exist
        if (!document.getElementById('auth-container')) {
            const authContainer = document.createElement('div');
            authContainer.id = 'auth-container';
            authContainer.className = 'auth-container';
            authContainer.innerHTML = `
                <div class="auth-box">
                    <h1 class="auth-title neon-text">Welcome to NeonChat</h1>
                    <p class="auth-subtitle">Your AI-Powered Journaling Companion</p>
                    
                    <div id="auth-form-container">
                        <!-- Dynamic form content -->
                    </div>
                </div>
            `;
            document.body.appendChild(authContainer);
        }

        this.renderLoginForm();
    }

    renderLoginForm() {
        const formContainer = document.getElementById('auth-form-container');
        formContainer.innerHTML = `
            <form id="login-form" class="auth-form">
                <h2>Login</h2>
                
                <div class="alert alert-info" style="background: rgba(0, 212, 255, 0.1); border: 1px solid #00d4ff; color: #00d4ff; padding: 1rem; margin-bottom: 1rem;">
                    <strong>Test Account:</strong><br>
                    Email: test@example.com<br>
                    Password: password
                </div>
                
                <div class="form-group">
                    <label for="login-email">Email</label>
                    <input type="email" id="login-email" class="form-control" required value="test@example.com">
                </div>
                
                <div class="form-group">
                    <label for="login-password">Password</label>
                    <input type="password" id="login-password" class="form-control" required value="password">
                </div>
                
                <div id="auth-error" class="alert alert-danger" style="display: none;"></div>
                
                <button type="submit" class="btn btn-primary btn-block">
                    <i class="fas fa-sign-in-alt"></i> Login
                </button>
                
                <p class="auth-switch">
                    Don't have an account? 
                    <a href="#" onclick="authUI.renderRegisterForm(); return false;">Register</a>
                </p>
            </form>
        `;

        // Bind login form events
        document.getElementById('login-form')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleLogin();
        });
    }

    renderRegisterForm() {
        const formContainer = document.getElementById('auth-form-container');
        formContainer.innerHTML = `
            <form id="register-form" class="auth-form">
                <h2>Create Account</h2>
                
                <div class="form-group">
                    <label for="register-name">Full Name</label>
                    <input type="text" id="register-name" class="form-control" required>
                </div>
                
                <div class="form-group">
                    <label for="register-email">Email</label>
                    <input type="email" id="register-email" class="form-control" required>
                </div>
                
                <div class="form-group">
                    <label for="register-password">Password</label>
                    <input type="password" id="register-password" class="form-control" required minlength="8">
                    <small class="form-text">Minimum 8 characters</small>
                </div>
                
                <div class="form-group">
                    <label for="register-confirm">Confirm Password</label>
                    <input type="password" id="register-confirm" class="form-control" required>
                </div>
                
                <div id="auth-error" class="alert alert-danger" style="display: none;"></div>
                
                <button type="submit" class="btn btn-primary btn-block">
                    <i class="fas fa-user-plus"></i> Create Account
                </button>
                
                <p class="auth-switch">
                    Already have an account? 
                    <a href="#" onclick="authUI.renderLoginForm(); return false;">Login</a>
                </p>
            </form>
        `;

        // Bind register form events
        document.getElementById('register-form')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleRegister();
        });
    }

    async handleLogin() {
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        console.log('Attempting login with:', email);

        // Show loading
        const submitBtn = document.querySelector('#login-form button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Logging in...';
        submitBtn.disabled = true;

        try {
            const result = await window.authService.login(email, password);
            console.log('Login result:', result);
            
            if (result.success) {
                this.showAuthenticatedUI();
                document.getElementById('auth-container')?.remove();
                document.querySelector('.main-content-revert').style.display = '';
                
                // Reload to update navigation
                window.location.reload();
            } else {
                this.showError(result.error || 'Login failed');
            }
        } catch (error) {
            console.error('Login error:', error);
            this.showError('Login failed. Please try again.');
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }

    async handleRegister() {
        const name = document.getElementById('register-name').value;
        const email = document.getElementById('register-email').value;
        const password = document.getElementById('register-password').value;
        const confirm = document.getElementById('register-confirm').value;

        // Validate passwords match
        if (password !== confirm) {
            this.showError('Passwords do not match');
            return;
        }

        // Show loading
        const submitBtn = document.querySelector('#register-form button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating account...';
        submitBtn.disabled = true;

        try {
            const result = await window.authService.register(email, password, name);
            
            if (result.success) {
                this.showAuthenticatedUI();
                document.getElementById('auth-container')?.remove();
                document.querySelector('.main-content-revert').style.display = '';
                
                // Show welcome message
                this.showWelcomeMessage(name);
            } else {
                this.showError(result.error || 'Registration failed');
            }
        } catch (error) {
            this.showError('Registration failed. Please try again.');
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }

    showAuthenticatedUI() {
        // Show user section in sidebar
        const userSection = document.getElementById('user-section');
        if (userSection && window.authService.user) {
            userSection.style.display = 'block';
            document.getElementById('user-email').textContent = window.authService.user.email;
        }

        // Enable protected navigation items
        document.getElementById('journal-nav')?.classList.remove('disabled');
        document.getElementById('metrics-nav')?.classList.remove('disabled');
    }

    showError(message) {
        const errorDiv = document.getElementById('auth-error');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                errorDiv.style.display = 'none';
            }, 5000);
        }
    }

    showWelcomeMessage(name) {
        const welcomeModal = document.createElement('div');
        welcomeModal.className = 'welcome-modal';
        welcomeModal.innerHTML = `
            <div class="welcome-content">
                <h2>Welcome to NeonChat, ${name}!</h2>
                <p>Your account has been created successfully.</p>
                <p>Start your journaling journey today:</p>
                <div class="welcome-actions">
                    <button class="btn btn-primary" onclick="journalUI.show(); this.parentElement.parentElement.parentElement.remove();">
                        <i class="fas fa-book"></i> Create First Entry
                    </button>
                    <button class="btn btn-secondary" onclick="metricsUI.show(); this.parentElement.parentElement.parentElement.remove();">
                        <i class="fas fa-chart-line"></i> Track Metrics
                    </button>
                    <button class="btn btn-ghost" onclick="this.parentElement.parentElement.parentElement.remove();">
                        <i class="fas fa-times"></i> Close
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(welcomeModal);
    }
}

// Create global instance
window.authUI = new AuthUI();