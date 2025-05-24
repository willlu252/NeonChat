// Helper function to get backend URL
function getBackendUrl() {
    return window.location.hostname === 'localhost' 
        ? 'http://localhost:8000'  // Backend URL in development
        : window.location.origin;   // Same origin in production
}

// Journal API Service
class JournalAPI {
    constructor() {
        this.baseUrl = getBackendUrl() + '/api/journal';
    }

    // Create a new journal entry
    async createEntry(entryData) {
        try {
            const response = await fetch(`${this.baseUrl}/entries`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(entryData)
            });

            if (!response.ok) {
                throw new Error('Failed to create journal entry');
            }

            return await response.json();
        } catch (error) {
            console.error('Create entry error:', error);
            throw error;
        }
    }

    // Get journal entries
    async getEntries(params = {}) {
        try {
            const queryParams = new URLSearchParams();
            if (params.limit) queryParams.append('limit', params.limit);
            if (params.offset) queryParams.append('offset', params.offset);
            if (params.startDate) queryParams.append('start_date', params.startDate);
            if (params.endDate) queryParams.append('end_date', params.endDate);
            if (params.moodMin) queryParams.append('mood_min', params.moodMin);
            if (params.moodMax) queryParams.append('mood_max', params.moodMax);

            const response = await fetch(`${this.baseUrl}/entries?${queryParams}`);

            if (!response.ok) {
                throw new Error('Failed to fetch journal entries');
            }

            return await response.json();
        } catch (error) {
            console.error('Get entries error:', error);
            throw error;
        }
    }

    // Get a specific journal entry
    async getEntry(entryId) {
        try {
            const response = await fetch(`${this.baseUrl}/entries/${entryId}`);

            if (!response.ok) {
                throw new Error('Failed to fetch journal entry');
            }

            return await response.json();
        } catch (error) {
            console.error('Get entry error:', error);
            throw error;
        }
    }

    // Update a journal entry
    async updateEntry(entryId, entryData) {
        try {
            const response = await fetch(`${this.baseUrl}/entries/${entryId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(entryData)
            });

            if (!response.ok) {
                throw new Error('Failed to update journal entry');
            }

            return await response.json();
        } catch (error) {
            console.error('Update entry error:', error);
            throw error;
        }
    }

    // Delete a journal entry
    async deleteEntry(entryId) {
        try {
            const response = await fetch(`${this.baseUrl}/entries/${entryId}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                throw new Error('Failed to delete journal entry');
            }

            return await response.json();
        } catch (error) {
            console.error('Delete entry error:', error);
            throw error;
        }
    }

    // Search entries by tags
    async searchByTags(tags) {
        try {
            const queryParams = new URLSearchParams();
            tags.forEach(tag => queryParams.append('tags', tag));

            const response = await fetch(`${this.baseUrl}/entries/search/tags?${queryParams}`);

            if (!response.ok) {
                throw new Error('Failed to search entries');
            }

            return await response.json();
        } catch (error) {
            console.error('Search by tags error:', error);
            throw error;
        }
    }

    // Get journal statistics
    async getStats(startDate, endDate) {
        try {
            const queryParams = new URLSearchParams();
            if (startDate) queryParams.append('start_date', startDate);
            if (endDate) queryParams.append('end_date', endDate);

            const response = await fetch(`${this.baseUrl}/entries/stats/summary?${queryParams}`);

            if (!response.ok) {
                throw new Error('Failed to fetch journal statistics');
            }

            return await response.json();
        } catch (error) {
            console.error('Get stats error:', error);
            throw error;
        }
    }

    // Analyze entry with MCP tools
    async analyzeEntry(entryText, previousMood = null) {
        try {
            const response = await fetch(`${getBackendUrl()}/mcp/tools/analyze_mood`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: entryText,
                    previous_mood: previousMood
                })
            });

            if (!response.ok) {
                throw new Error('Failed to analyze entry');
            }

            return await response.json();
        } catch (error) {
            console.error('Analyze entry error:', error);
            return null; // Return null on error to allow graceful degradation
        }
    }

    // Generate tags for entry
    async generateTags(entryText) {
        try {
            const response = await fetch(`${getBackendUrl()}/mcp/tools/generate_tags`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: entryText,
                    max_tags: 5
                })
            });

            if (!response.ok) {
                throw new Error('Failed to generate tags');
            }

            return await response.json();
        } catch (error) {
            console.error('Generate tags error:', error);
            return []; // Return empty array on error
        }
    }

    // Get AI insights for entry
    async getAIInsights(entryText, moodScore, metrics = null) {
        try {
            const response = await fetch(`${getBackendUrl()}/mcp/tools/generate_ai_insights`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    entry_text: entryText,
                    mood_score: moodScore,
                    metrics: metrics
                })
            });

            if (!response.ok) {
                throw new Error('Failed to get AI insights');
            }

            return await response.json();
        } catch (error) {
            console.error('Get AI insights error:', error);
            return null;
        }
    }

    // Get journal prompts
    async getJournalPrompts(mood, recentTopics = []) {
        try {
            const response = await fetch(`${getBackendUrl()}/mcp/tools/suggest_prompts`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    mood: mood,
                    recent_topics: recentTopics
                })
            });

            if (!response.ok) {
                throw new Error('Failed to get journal prompts');
            }

            return await response.json();
        } catch (error) {
            console.error('Get prompts error:', error);
            return [];
        }
    }
}

// Metrics API Service
class MetricsAPI {
    constructor() {
        this.baseUrl = getBackendUrl() + '/api/metrics';
    }

    // Create or update daily metrics
    async saveDailyMetrics(metrics) {
        try {
            const response = await fetch(`${this.baseUrl}/daily`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(metrics)
            });

            if (!response.ok) {
                throw new Error('Failed to save daily metrics');
            }

            return await response.json();
        } catch (error) {
            console.error('Save metrics error:', error);
            throw error;
        }
    }

    // Get daily metrics
    async getDailyMetrics(params = {}) {
        try {
            const queryParams = new URLSearchParams();
            if (params.startDate) queryParams.append('start_date', params.startDate);
            if (params.endDate) queryParams.append('end_date', params.endDate);
            if (params.limit) queryParams.append('limit', params.limit);
            if (params.offset) queryParams.append('offset', params.offset);

            const response = await fetch(`${this.baseUrl}/daily?${queryParams}`);

            if (!response.ok) {
                throw new Error('Failed to fetch daily metrics');
            }

            return await response.json();
        } catch (error) {
            console.error('Get metrics error:', error);
            throw error;
        }
    }

    // Get metrics for specific date
    async getMetricsByDate(date) {
        try {
            const response = await fetch(`${this.baseUrl}/daily/${date}`);

            if (!response.ok) {
                if (response.status === 404) {
                    return null; // No metrics for this date
                }
                throw new Error('Failed to fetch metrics');
            }

            return await response.json();
        } catch (error) {
            console.error('Get metrics by date error:', error);
            throw error;
        }
    }

    // Get weekly trends
    async getWeeklyTrends(weeks = 4) {
        try {
            const response = await fetch(`${this.baseUrl}/trends/weekly?weeks=${weeks}`);

            if (!response.ok) {
                throw new Error('Failed to fetch weekly trends');
            }

            return await response.json();
        } catch (error) {
            console.error('Get trends error:', error);
            throw error;
        }
    }

    // Get insights
    async getInsights(days = 30) {
        try {
            const response = await fetch(`${this.baseUrl}/insights?days=${days}`);

            if (!response.ok) {
                throw new Error('Failed to fetch insights');
            }

            return await response.json();
        } catch (error) {
            console.error('Get insights error:', error);
            throw error;
        }
    }

    // Calculate wellbeing score
    async calculateWellbeing(metrics) {
        try {
            const response = await fetch(`${getBackendUrl()}/mcp/tools/calculate_wellbeing`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ metrics })
            });

            if (!response.ok) {
                throw new Error('Failed to calculate wellbeing');
            }

            return await response.json();
        } catch (error) {
            console.error('Calculate wellbeing error:', error);
            return null;
        }
    }
}

// Create global instances
window.journalAPI = new JournalAPI();
window.metricsAPI = new MetricsAPI();