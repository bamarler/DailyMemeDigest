/**
 * API handling for AI Meme Newsletter
 * Handles all communication with Flask backend
 */

class MemeAPI {
    constructor() {
        this.baseURL = '';  // Same origin
    }

    /**
     * Generate memes from selected trends and duration
     * 
     * @param {Array} trends - Selected AI trends
     * @param {number} duration - Duration in days
     * @param {number} memes - Number of memes
     * @returns {Promise<Array>} Generated memes
     */
    async generateMemes(trends, duration, memes) {
        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    trends: trends,
                    duration: duration,
                    memes: memes
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('API Response:', data);
            
            if (!data.success) {
                throw new Error(data.error || 'Failed to generate memes');
            }
            
            return data.memes;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    /**
     * Get existing memes from the database
     * 
     * @returns {Promise<Object>} Response with memes array and metadata
     */
    async getMemes() {
        try {
            const response = await fetch(`/api/memes`);


            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Ensure we return the expected structure
            return {
                success: data.success || true,
                memes: data.memes || [],
                total_count: data.total_count || 0
            };
        } catch (error) {
            console.error('Error fetching memes:', error);
            return {
                success: false,
                memes: [],
                error: error.message
            };
        }
    }

    /**
     * Get recent news articles
     * 
     * @param {number} duration - Duration in days
     * @returns {Promise<Array>} News articles
     */
    async getNews(duration = 1) {
        try {
            const response = await fetch(`/api/news?duration=${duration}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            return data.news || [];
        } catch (error) {
            console.error('Error fetching news:', error);
            return [];
        }
    }

    /**
     * Health check endpoint
     * 
     * @returns {Promise<Object>} Health status
     */
    async healthCheck() {
        try {
            const response = await fetch('/api/health');
            return await response.json();
        } catch (error) {
            console.error('Health check failed:', error);
            return { status: 'error', error: error.message };
        }
    }
}

// Create global API instance
window.memeAPI = new MemeAPI();

// Export for module usage if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MemeAPI;
}