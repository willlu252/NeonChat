// Metrics UI Components and Controllers
class MetricsUI {
    constructor() {
        this.currentDate = new Date().toISOString().split('T')[0];
        this.currentMetrics = null;
        this.init();
    }

    init() {
        // Initialize with existing container
        this.ensureMetricsStructure();
        this.bindEvents();
    }

    ensureMetricsStructure() {
        const container = document.getElementById('metrics-container');
        if (container && !container.querySelector('.metrics-header')) {
            container.innerHTML = `
                <div class="metrics-header">
                    <h2>Daily Metrics</h2>
                    <div class="metrics-nav">
                        <button id="metrics-today-btn" class="btn btn-primary">Today</button>
                        <button id="metrics-trends-btn" class="btn btn-secondary">Trends</button>
                        <button id="metrics-insights-btn" class="btn btn-secondary">Insights</button>
                    </div>
                </div>
                <div id="metrics-content" class="metrics-content">
                    <!-- Dynamic content goes here -->
                </div>
            `;
        }
    }

    bindEvents() {
        document.getElementById('metrics-today-btn')?.addEventListener('click', () => {
            this.showDailyForm();
        });

        document.getElementById('metrics-trends-btn')?.addEventListener('click', () => {
            this.showTrends();
        });

        document.getElementById('metrics-insights-btn')?.addEventListener('click', () => {
            this.showInsights();
        });
    }

    // Show metrics UI
    show() {
        document.getElementById('metrics-container')?.classList.remove('hidden');
        document.getElementById('journal-container')?.classList.add('hidden');
        document.body.classList.add('metrics-active');
        this.showDailyForm();
    }

    // Hide metrics UI
    hide() {
        document.getElementById('metrics-container')?.classList.add('hidden');
        document.body.classList.remove('metrics-active');
    }

    // Show daily metrics form
    async showDailyForm(date = null) {
        const targetDate = date || this.currentDate;
        
        // Load existing metrics for the date
        try {
            this.currentMetrics = await window.metricsAPI.getMetricsByDate(targetDate);
        } catch (error) {
            console.error('Failed to load metrics:', error);
            this.currentMetrics = null;
        }

        const metrics = this.currentMetrics || {};
        const content = document.getElementById('metrics-content');
        
        content.innerHTML = `
            <div class="metrics-form-container">
                <div class="date-selector">
                    <button class="btn btn-sm" id="date-prev-btn">
                        <i class="fas fa-chevron-left"></i>
                    </button>
                    <input type="date" id="metrics-date" value="${targetDate}" 
                           max="${new Date().toISOString().split('T')[0]}">
                    <button class="btn btn-sm" id="date-next-btn">
                        <i class="fas fa-chevron-right"></i>
                    </button>
                </div>
                
                <form id="metrics-form">
                    <div class="metrics-section">
                        <h3><i class="fas fa-bed"></i> Physical Health</h3>
                        
                        <div class="metric-group">
                            <label for="sleep-hours">
                                Sleep Hours
                                <span class="metric-value">${metrics.sleep_hours || 0}</span>
                            </label>
                            <input type="range" id="sleep-hours" name="sleep_hours" 
                                   min="0" max="12" step="0.5" value="${metrics.sleep_hours || 0}">
                        </div>
                        
                        <div class="metric-group">
                            <label for="water-intake">
                                Water Intake (glasses)
                                <span class="metric-value">${metrics.water_intake || 0}</span>
                            </label>
                            <input type="range" id="water-intake" name="water_intake" 
                                   min="0" max="16" value="${metrics.water_intake || 0}">
                        </div>
                        
                        <div class="metric-group">
                            <label for="exercise-minutes">
                                Exercise Minutes
                                <span class="metric-value">${metrics.exercise_minutes || 0}</span>
                            </label>
                            <input type="range" id="exercise-minutes" name="exercise_minutes" 
                                   min="0" max="120" step="5" value="${metrics.exercise_minutes || 0}">
                        </div>
                        
                        <div class="metric-group">
                            <label for="steps">
                                Steps
                                <span class="metric-value">${metrics.steps || 0}</span>
                            </label>
                            <input type="number" id="steps" name="steps" 
                                   min="0" max="50000" value="${metrics.steps || 0}" class="form-control">
                        </div>
                    </div>
                    
                    <div class="metrics-section">
                        <h3><i class="fas fa-brain"></i> Mental & Emotional</h3>
                        
                        <div class="metric-group">
                            <label for="stress-level">
                                Stress Level (1-10)
                                <span class="metric-value">${metrics.stress_level || 5}</span>
                            </label>
                            <input type="range" id="stress-level" name="stress_level" 
                                   min="1" max="10" value="${metrics.stress_level || 5}">
                        </div>
                        
                        <div class="metric-group">
                            <label for="anxiety-level">
                                Anxiety Level (1-10)
                                <span class="metric-value">${metrics.anxiety_level || 5}</span>
                            </label>
                            <input type="range" id="anxiety-level" name="anxiety_level" 
                                   min="1" max="10" value="${metrics.anxiety_level || 5}">
                        </div>
                        
                        <div class="metric-group">
                            <label for="happiness-level">
                                Happiness Level (1-10)
                                <span class="metric-value">${metrics.happiness_level || 5}</span>
                            </label>
                            <input type="range" id="happiness-level" name="happiness_level" 
                                   min="1" max="10" value="${metrics.happiness_level || 5}">
                        </div>
                        
                        <div class="metric-group">
                            <label for="meditation-minutes">
                                Meditation Minutes
                                <span class="metric-value">${metrics.meditation_minutes || 0}</span>
                            </label>
                            <input type="range" id="meditation-minutes" name="meditation_minutes" 
                                   min="0" max="60" value="${metrics.meditation_minutes || 0}">
                        </div>
                    </div>
                    
                    <div class="metrics-section">
                        <h3><i class="fas fa-users"></i> Social & Work</h3>
                        
                        <div class="metric-group">
                            <label for="social-quality">
                                Social Interaction Quality (1-10)
                                <span class="metric-value">${metrics.social_interaction_quality || 5}</span>
                            </label>
                            <input type="range" id="social-quality" name="social_interaction_quality" 
                                   min="1" max="10" value="${metrics.social_interaction_quality || 5}">
                        </div>
                        
                        <div class="metric-group">
                            <label for="work-satisfaction">
                                Work Satisfaction (1-10)
                                <span class="metric-value">${metrics.work_satisfaction || 5}</span>
                            </label>
                            <input type="range" id="work-satisfaction" name="work_satisfaction" 
                                   min="1" max="10" value="${metrics.work_satisfaction || 5}">
                        </div>
                        
                        <div class="metric-group">
                            <label for="productivity-score">
                                Productivity Score (1-10)
                                <span class="metric-value">${metrics.productivity_score || 5}</span>
                            </label>
                            <input type="range" id="productivity-score" name="productivity_score" 
                                   min="1" max="10" value="${metrics.productivity_score || 5}">
                        </div>
                        
                        <div class="metric-group">
                            <label for="prayer-minutes">
                                Prayer/Spiritual Minutes
                                <span class="metric-value">${metrics.prayer_minutes || 0}</span>
                            </label>
                            <input type="range" id="prayer-minutes" name="prayer_minutes" 
                                   min="0" max="60" value="${metrics.prayer_minutes || 0}">
                        </div>
                    </div>
                    
                    <div class="wellbeing-display" id="wellbeing-display" style="display: ${metrics.wellbeing_score ? 'block' : 'none'}">
                        <h3>Wellbeing Score</h3>
                        <div class="wellbeing-score-circle">
                            <span class="score">${metrics.wellbeing_score || 0}</span>
                            <span class="out-of">/10</span>
                        </div>
                    </div>
                    
                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-save"></i> Save Metrics
                        </button>
                        <button type="button" class="btn btn-secondary" id="calculate-wellbeing-btn">
                            <i class="fas fa-calculator"></i> Calculate Wellbeing
                        </button>
                    </div>
                </form>
            </div>
        `;

        this.bindFormEvents();
    }

    // Bind form events
    bindFormEvents() {
        // Date change
        document.getElementById('metrics-date')?.addEventListener('change', (e) => {
            this.currentDate = e.target.value;
            this.showDailyForm(this.currentDate);
        });

        // Date navigation buttons
        document.getElementById('date-prev-btn')?.addEventListener('click', () => {
            this.changeDate(-1);
        });

        document.getElementById('date-next-btn')?.addEventListener('click', () => {
            this.changeDate(1);
        });

        // Calculate wellbeing button
        document.getElementById('calculate-wellbeing-btn')?.addEventListener('click', () => {
            this.calculateWellbeing();
        });

        // Update metrics button (in insights view)
        document.getElementById('update-metrics-btn')?.addEventListener('click', () => {
            this.showDailyForm();
        });

        // Write journal button (in insights view)
        document.getElementById('write-journal-btn')?.addEventListener('click', () => {
            if (window.journalUI) {
                window.journalUI.show();
            }
        });

        // Form submission
        document.getElementById('metrics-form')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.saveMetrics();
        });

        // Range inputs - update display values
        document.querySelectorAll('input[type="range"]').forEach(input => {
            input.addEventListener('input', (e) => {
                const label = e.target.parentElement.querySelector('.metric-value');
                if (label) {
                    label.textContent = e.target.value;
                }
            });
        });
    }

    // Change date
    changeDate(days) {
        const currentDate = new Date(this.currentDate);
        currentDate.setDate(currentDate.getDate() + days);
        
        // Don't go beyond today
        const today = new Date();
        if (currentDate > today) {
            currentDate.setTime(today.getTime());
        }
        
        this.currentDate = currentDate.toISOString().split('T')[0];
        this.showDailyForm(this.currentDate);
    }

    // Save metrics
    async saveMetrics() {
        const form = document.getElementById('metrics-form');
        const formData = new FormData(form);
        
        const metrics = {
            date: this.currentDate
        };
        
        // Convert form data to metrics object
        for (let [key, value] of formData.entries()) {
            metrics[key] = parseFloat(value) || 0;
        }

        try {
            const result = await window.metricsAPI.saveDailyMetrics(metrics);
            
            // Update wellbeing display
            if (result.wellbeing_score) {
                this.displayWellbeing(result.wellbeing_score);
            }
            
            // Show success message
            this.showMessage('Metrics saved successfully!', 'success');
            
            // Update current metrics
            this.currentMetrics = result;
        } catch (error) {
            console.error('Failed to save metrics:', error);
            this.showMessage('Failed to save metrics', 'error');
        }
    }

    // Calculate wellbeing
    async calculateWellbeing() {
        const form = document.getElementById('metrics-form');
        const formData = new FormData(form);
        
        const metrics = {};
        for (let [key, value] of formData.entries()) {
            metrics[key] = parseFloat(value) || 0;
        }

        try {
            const result = await window.metricsAPI.calculateWellbeing(metrics);
            
            if (result && result.wellbeing_score) {
                this.displayWellbeing(result.wellbeing_score);
                
                // Show insights if available
                if (result.insights && result.insights.length > 0) {
                    this.showQuickInsights(result.insights);
                }
            }
        } catch (error) {
            console.error('Failed to calculate wellbeing:', error);
        }
    }

    // Display wellbeing score
    displayWellbeing(score) {
        const display = document.getElementById('wellbeing-display');
        if (display) {
            display.style.display = 'block';
            display.querySelector('.score').textContent = score;
            
            // Add color based on score
            const circle = display.querySelector('.wellbeing-score-circle');
            circle.className = 'wellbeing-score-circle';
            if (score >= 8) {
                circle.classList.add('excellent');
            } else if (score >= 6) {
                circle.classList.add('good');
            } else if (score >= 4) {
                circle.classList.add('fair');
            } else {
                circle.classList.add('poor');
            }
        }
    }

    // Show trends
    async showTrends() {
        try {
            const trends = await window.metricsAPI.getWeeklyTrends(4);
            const content = document.getElementById('metrics-content');
            
            content.innerHTML = `
                <div class="trends-container">
                    <h3>Weekly Trends</h3>
                    
                    <div class="overall-averages">
                        <h4>Overall Averages (Last 4 Weeks)</h4>
                        <div class="averages-grid">
                            <div class="average-item">
                                <i class="fas fa-heart"></i>
                                <span class="value">${trends.overall_averages.wellbeing || 'N/A'}</span>
                                <span class="label">Wellbeing</span>
                            </div>
                            <div class="average-item">
                                <i class="fas fa-bed"></i>
                                <span class="value">${trends.overall_averages.sleep || 'N/A'}</span>
                                <span class="label">Sleep (hrs)</span>
                            </div>
                            <div class="average-item">
                                <i class="fas fa-brain"></i>
                                <span class="value">${trends.overall_averages.stress || 'N/A'}</span>
                                <span class="label">Stress</span>
                            </div>
                            <div class="average-item">
                                <i class="fas fa-smile"></i>
                                <span class="value">${trends.overall_averages.happiness || 'N/A'}</span>
                                <span class="label">Happiness</span>
                            </div>
                            <div class="average-item">
                                <i class="fas fa-running"></i>
                                <span class="value">${trends.overall_averages.exercise || 'N/A'}</span>
                                <span class="label">Exercise (min)</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="weekly-breakdown">
                        <h4>Weekly Breakdown</h4>
                        <div class="weeks-list">
                            ${trends.weeks.map(week => `
                                <div class="week-item">
                                    <div class="week-header">
                                        Week of ${new Date(week.week_start).toLocaleDateString()}
                                        <span class="days-tracked">${week.metrics_count} days tracked</span>
                                    </div>
                                    <div class="week-metrics">
                                        <span>Wellbeing: ${week.avg_wellbeing}</span>
                                        <span>Sleep: ${week.avg_sleep}h</span>
                                        <span>Stress: ${week.avg_stress}</span>
                                        <span>Exercise: ${week.avg_exercise}min</span>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    
                    <div class="chart-container">
                        <canvas id="trends-chart"></canvas>
                    </div>
                </div>
            `;
            
            // Draw trends chart if data available
            if (trends.weeks.length > 0) {
                this.drawTrendsChart(trends.weeks);
            }
        } catch (error) {
            console.error('Failed to load trends:', error);
            this.showError('Failed to load trends');
        }
    }

    // Show insights
    async showInsights() {
        try {
            const insights = await window.metricsAPI.getInsights(30);
            const content = document.getElementById('metrics-content');
            
            content.innerHTML = `
                <div class="insights-container">
                    <h3>Your Health Insights</h3>
                    
                    <div class="insights-summary">
                        <p>Based on ${insights.summary.days_tracked} days of tracking</p>
                        ${insights.summary.avg_wellbeing ? 
                            `<p>Average wellbeing score: <strong>${insights.summary.avg_wellbeing}/10</strong></p>` : ''}
                    </div>
                    
                    <div class="insights-list">
                        <h4>Key Insights</h4>
                        ${insights.insights.map(insight => `
                            <div class="insight-item">
                                <i class="fas fa-lightbulb"></i>
                                <p>${insight}</p>
                            </div>
                        `).join('')}
                    </div>
                    
                    <div class="recommendations-list">
                        <h4>Recommendations</h4>
                        ${insights.recommendations.map(rec => `
                            <div class="recommendation-item">
                                <i class="fas fa-check-circle"></i>
                                <p>${rec}</p>
                            </div>
                        `).join('')}
                    </div>
                    
                    <div class="action-buttons">
                        <button class="btn btn-primary" id="update-metrics-btn">
                            <i class="fas fa-edit"></i> Update Today's Metrics
                        </button>
                        <button class="btn btn-secondary" id="write-journal-btn">
                            <i class="fas fa-book"></i> Write Journal Entry
                        </button>
                    </div>
                </div>
            `;
            
            // Bind event listeners for the insights view buttons
            document.getElementById('update-metrics-btn')?.addEventListener('click', () => {
                this.showDailyForm();
            });

            document.getElementById('write-journal-btn')?.addEventListener('click', () => {
                if (window.journalUI) {
                    window.journalUI.show();
                }
            });
        } catch (error) {
            console.error('Failed to load insights:', error);
            this.showError('Failed to load insights');
        }
    }

    // Show quick insights
    showQuickInsights(insights) {
        const modal = document.createElement('div');
        modal.className = 'quick-insights-modal';
        modal.innerHTML = `
            <div class="quick-insights-content">
                <h4>Quick Insights</h4>
                ${insights.map(insight => `<p>${insight}</p>`).join('')}
                <button class="btn btn-primary" onclick="this.parentElement.parentElement.remove()">OK</button>
            </div>
        `;
        document.body.appendChild(modal);
        
        // Auto-remove after 10 seconds
        setTimeout(() => modal.remove(), 10000);
    }

    // Helper methods
    showMessage(message, type = 'info') {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="close" onclick="this.parentElement.remove()">
                <span>&times;</span>
            </button>
        `;
        
        const content = document.getElementById('metrics-content');
        content.insertBefore(alert, content.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => alert.remove(), 5000);
    }

    showError(message) {
        const content = document.getElementById('metrics-content');
        content.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle"></i> ${message}
            </div>
        `;
    }

    drawTrendsChart(weeks) {
        // Implement chart drawing if Chart.js is available
        // This is a placeholder for chart implementation
    }
}

// Create global instance
window.metricsUI = new MetricsUI();