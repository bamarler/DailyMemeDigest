/**
 * Main application initialization for AI Meme Newsletter
 * Coordinates between UI and API components
 */

class MemeApp {
    constructor() {
        this.isInitialized = false;
        this.version = '1.0.0';
    }

    /**
     * Initialize the application
     */
    async init() {
        if (this.isInitialized) {
            console.warn('App already initialized');
            return;
        }

        try {
            console.log('🎭 AI Meme Newsletter v' + this.version + ' initializing...');
            
            // Check if dependencies are loaded
            this.checkDependencies();
            
            // Initialize components
            await this.initializeComponents();
            
            // Setup global error handling
            this.setupErrorHandling();
            
            // Perform health check
            await this.performHealthCheck();
            
            // Initialize entrance animations
            window.memeUI.initializeAnimations();
            
            this.isInitialized = true;
            console.log('✅ AI Meme Newsletter initialized successfully');
            
        } catch (error) {
            console.error('❌ Failed to initialize app:', error);
            this.handleInitializationError(error);
        }
    }

    /**
     * Check if all required dependencies are loaded
     */
    checkDependencies() {
        const requiredGlobals = ['memeAPI', 'memeUI'];
        const missing = requiredGlobals.filter(global => !window[global]);
        
        if (missing.length > 0) {
            throw new Error(`Missing required dependencies: ${missing.join(', ')}`);
        }
    }

    /**
     * Initialize application components
     */
    async initializeComponents() {
        // Components are already initialized via their constructors
        // This is where you'd add any additional setup
        
        // Example: Load user preferences
        this.loadUserPreferences();
        
        // Example: Setup analytics
        this.setupAnalytics();
    }

    /**
     * Setup global error handling
     */
    setupErrorHandling() {
        // Handle uncaught JavaScript errors
        window.addEventListener('error', (event) => {
            console.error('Global error:', event.error);
            window.memeUI.showAlert('Something went wrong. Please refresh the page.', 'error');
        });

        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            window.memeUI.showAlert('An unexpected error occurred.', 'error');
        });
    }

    /**
     * Perform application health check
     */
    async performHealthCheck() {
        try {
            const health = await window.memeAPI.healthCheck();
            console.log('🔍 Health check:', health);
            
            if (health.status !== 'healthy') {
                console.warn('Backend health check failed:', health);
            }
        } catch (error) {
            console.warn('Health check failed:', error);
            // Don't throw error here as the app can still function
        }
    }

    /**
     * Handle initialization errors
     */
    handleInitializationError(error) {
        // Show user-friendly error message
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: #ff416c;
            color: white;
            padding: 20px;
            text-align: center;
            z-index: 9999;
            font-family: Arial, sans-serif;
        `;
        errorDiv.innerHTML = `
            <h3>⚠️ Application Error</h3>
            <p>Failed to initialize the AI Meme Newsletter. Please refresh the page.</p>
            <button onclick="window.location.reload()" style="
                background: white;
                color: #ff416c;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                margin-top: 10px;
                cursor: pointer;
                font-weight: bold;
            ">Refresh Page</button>
        `;
        
        document.body.insertBefore(errorDiv, document.body.firstChild);
    }

    /**
     * Load user preferences from localStorage
     */
    loadUserPreferences() {
        try {
            const preferences = localStorage.getItem('memePreferences');
            if (preferences) {
                const parsed = JSON.parse(preferences);
                console.log('📋 Loaded user preferences:', parsed);
                
                // Apply preferences
                if (parsed.selectedTrends) {
                    window.memeUI.selectedTrends = parsed.selectedTrends;
                    window.memeUI.updateSelectedTags();
                }
                
                if (parsed.selectedDuration) {
                    window.memeUI.selectedDuration = parsed.selectedDuration;
                    // Update UI to reflect saved duration
                    this.updateDurationUI(parsed.selectedDuration);
                }
            }
        } catch (error) {
            console.warn('Failed to load user preferences:', error);
        }
    }

    /**
     * Save user preferences to localStorage
     */
    saveUserPreferences() {
        try {
            const preferences = {
                selectedTrends: window.memeUI.selectedTrends,
                selectedDuration: window.memeUI.selectedDuration,
                savedAt: new Date().toISOString()
            };
            
            localStorage.setItem('memePreferences', JSON.stringify(preferences));
            console.log('💾 Saved user preferences');
        } catch (error) {
            console.warn('Failed to save user preferences:', error);
        }
    }

    /**
     * Update duration UI based on saved preference
     */
    updateDurationUI(duration) {
        const buttons = document.querySelectorAll('.duration-btn');
        buttons.forEach(btn => {
            btn.classList.remove('active');
            if (parseInt(btn.getAttribute('data-duration')) === duration) {
                btn.classList.add('active');
            }
        });
    }

    /**
     * Setup analytics tracking
     */
    setupAnalytics() {
        // Example analytics setup
        console.log('📊 Analytics initialized');
        
        // Track page load
        window.memeUI.trackEvent('app_initialized', {
            version: this.version,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent.substring(0, 100)
        });
    }

    /**
     * Auto-save preferences when they change
     */
    setupAutoSave() {
        // Save preferences when trends change
        const originalSelectTrend = window.memeUI.selectTrend;
        window.memeUI.selectTrend = function(trend) {
            originalSelectTrend.call(this, trend);
            window.memeApp.saveUserPreferences();
        };

        const originalRemoveTrend = window.memeUI.removeTrend;
        window.memeUI.removeTrend = function(trend) {
            originalRemoveTrend.call(this, trend);
            window.memeApp.saveUserPreferences();
        };

        const originalSelectDuration = window.memeUI.selectDuration;
        window.memeUI.selectDuration = function(button, duration) {
            originalSelectDuration.call(this, button, duration);
            window.memeApp.saveUserPreferences();
        };
    }

    /**
     * Get application info
     */
    getInfo() {
        return {
            name: 'AI Meme Newsletter',
            version: this.version,
            initialized: this.isInitialized,
            dependencies: {
                api: !!window.memeAPI,
                ui: !!window.memeUI
            },
            features: {
                localStorage: this.hasLocalStorage(),
                intersectionObserver: 'IntersectionObserver' in window,
                fetch: 'fetch' in window,
                webGL: this.hasWebGL()
            }
        };
    }

    /**
     * Check if localStorage is available
     */
    hasLocalStorage() {
        try {
            const test = '__test__';
            localStorage.setItem(test, test);
            localStorage.removeItem(test);
            return true;
        } catch (e) {
            return false;
        }
    }

    /**
     * Check if WebGL is available
     */
    hasWebGL() {
        try {
            const canvas = document.createElement('canvas');
            return !!(canvas.getContext('webgl') || canvas.getContext('experimental-webgl'));
        } catch (e) {
            return false;
        }
    }

    /**
     * Cleanup resources (useful for SPA navigation)
     */
    destroy() {
        console.log('🧹 Cleaning up AI Meme Newsletter...');
        
        // Remove event listeners
        // Clear timers/intervals
        // Clear global references
        
        this.isInitialized = false;
    }
}

// Create global app instance
window.memeApp = new MemeApp();

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.memeApp.init();
    });
} else {
    // DOM is already ready
    window.memeApp.init();
}

// Setup auto-save after initialization
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        if (window.memeApp.isInitialized) {
            window.memeApp.setupAutoSave();
        }
    }, 1000);
});

// Expose app info to console for debugging
console.log('🎭 AI Meme Newsletter loaded. Type memeApp.getInfo() for details.');