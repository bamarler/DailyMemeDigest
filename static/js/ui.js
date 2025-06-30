/**
 * UI interactions for AI Meme Newsletter
 * Handles all user interface logic for the main page
 */

class MemeUI {
    constructor() {
        this.selectedTrends = [];
        this.selectedDuration = 1;
        this.selectedMemes = 1;
        this.generatedMemes = [];
        
        console.log('🎨 MemeUI initializing...');
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }

    /**
     * Initialize UI components
     */
    init() {
        console.log('🎨 MemeUI init called');
        this.initializeEventListeners();
        this.setupAccessibility();
        console.log('✅ MemeUI initialized successfully');
    }

    /**
     * Initialize all event listeners
     */
    initializeEventListeners() {
        const dropdownButton = document.getElementById('dropdownButton');
        const dropdownMenu = document.getElementById('dropdownMenu');
        
        if (dropdownButton) {
            dropdownButton.addEventListener('click', () => this.toggleDropdown());
        }

        const dropdownItems = document.querySelectorAll('.dropdown-item');
        dropdownItems.forEach(item => {
            item.addEventListener('click', (e) => {
                const trend = e.target.getAttribute('data-trend');
                this.selectTrend(trend);
            });
        });

        const durationButtons = document.querySelectorAll('.duration-btn');
        durationButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const duration = parseInt(e.target.getAttribute('data-duration'));
                this.selectDuration(e.target, duration);
            });
        });

        const memesButtons = document.querySelectorAll('.memes-btn');
        memesButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const memes = parseInt(e.target.getAttribute('data-memes'));
                this.selectMemes(e.target, memes);
            });
        });

        const generateBtn = document.getElementById('generateBtn');
        if (generateBtn) {
            generateBtn.addEventListener('click', () => this.handleGenerateMemes());
        }

        const backBtn = document.getElementById('backBtn');
        if (backBtn) {
            backBtn.addEventListener('click', () => this.goBack());
        }

        document.addEventListener('click', (event) => {
            const dropdown = document.querySelector('.dropdown-container');
            if (dropdown && !dropdown.contains(event.target)) {
                this.closeDropdown();
            }
        });

        document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));

        window.addEventListener('online', () => {
            this.showAlert('🌐 Connection restored!', 'success');
        });

        window.addEventListener('offline', () => {
            this.showAlert('🚫 No internet connection. Please check your network.', 'error');
        });

        document.addEventListener('visibilitychange', () => {
            this.handleVisibilityChange();
        });

        this.setupTouchSupport();
        this.setupEasterEgg();
    }

    /**
     * Toggle dropdown menu
     */
    toggleDropdown() {
        const menu = document.getElementById('dropdownMenu');
        const button = document.getElementById('dropdownButton');
        const isActive = menu.classList.contains('active');
        
        if (isActive) {
            menu.classList.remove('active');
            button.classList.remove('active');
        } else {
            menu.classList.add('active');
            button.classList.add('active');
        }

        button.setAttribute('aria-expanded', !isActive);
    }

    /**
     * Close dropdown menu
     */
    closeDropdown() {
        const menu = document.getElementById('dropdownMenu');
        const button = document.getElementById('dropdownButton');
        
        if (menu && button) {
            menu.classList.remove('active');
            button.classList.remove('active');
            button.setAttribute('aria-expanded', 'false');
        }
    }

    /**
     * Select a trend from dropdown
     * @param {string} trend - The selected trend
     */
    selectTrend(trend) {
        if (!this.selectedTrends.includes(trend)) {
            this.selectedTrends.push(trend);
            this.updateSelectedTags();
            this.trackEvent('trend_selected', { trend });
        }
        this.closeDropdown();
    }

    /**
     * Remove a selected trend
     * @param {string} trend - The trend to remove
     */
    removeTrend(trend) {
        this.selectedTrends = this.selectedTrends.filter(t => t !== trend);
        this.updateSelectedTags();
    }

    /**
     * Update the display of selected tags
     */
    updateSelectedTags() {
        const container = document.getElementById('selectedTags');
        if (!container) return;

        container.innerHTML = this.selectedTrends.map(trend => 
            `<div class="tag">
                ${trend}
                <span class="remove" onclick="window.memeUI.removeTrend('${trend.replace(/'/g, "\\'")}')">×</span>
            </div>`
        ).join('');
    }

    /**
     * Select duration
     * @param {HTMLElement} button - The clicked button
     * @param {number} duration - Duration in days
     */
    selectDuration(button, duration) {
        document.querySelectorAll('.duration-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        button.classList.add('active');
        this.selectedDuration = duration;
    }

    /**
     * Select memes
     * @param {HTMLElement} button - The clicked button
     * @param {number} memes - Number of memes
     */
    selectMemes(button, memes) {
        document.querySelectorAll('.memes-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        button.classList.add('active');
        this.selectedMemes = memes;
    }

    /**
     * Handle meme generation
     */
    async handleGenerateMemes() {
        if (this.selectedTrends.length === 0) {
            this.showAlert('Please select at least one AI trend!', 'warning');
            return;
        }

        this.trackEvent('memes_generation_started', { 
            trends: this.selectedTrends,
            duration: this.selectedDuration,
            memes: this.selectedMemes 
        });

        this.showLoading();
        
        try {
            await this.updateProgress(20, 'Fetching latest AI news...');
            await this.sleep(1000);
            
            await this.updateProgress(40, 'Analyzing news articles with AI...');
            await this.sleep(1000);
            
            await this.updateProgress(60, 'Generating meme prompts...');
            
            const memes = await window.memeAPI.generateMemes(this.selectedTrends, this.selectedDuration, this.selectedMemes);
            
            await this.updateProgress(100, 'Memes ready!');
            await this.sleep(500);
            
            this.generatedMemes = memes;
            this.showMemesPage();
            
            const successCount = memes.filter(m => m.success).length;
            this.showAlert(`🎉 Successfully generated ${successCount} memes!`, 'success');
            
        } catch (error) {
            console.error('Error generating memes:', error);
            this.showAlert(`Failed to generate memes: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }

    /**
     * Show memes page
     */
    showMemesPage() {
        document.getElementById('landingPage').style.display = 'none';
        document.getElementById('memesPage').style.display = 'block';
        
        this.renderMemes();
        
        window.scrollTo(0, 0);
    }

    /**
     * Go back to landing page
     */
    goBack() {
        document.getElementById('memesPage').style.display = 'none';
        document.getElementById('landingPage').style.display = 'block';
        
        window.scrollTo(0, 0);
    }

    /**
     * Render generated memes
     */
    renderMemes() {
        const container = document.getElementById('memesGrid');
        if (!container) return;
        
        if (this.generatedMemes.length === 0) {
            container.innerHTML = `
                <div class="error-card">
                    <div class="error-content">
                        <h3>🤔 No Memes Generated</h3>
                        <p>Try selecting different trends or adjusting the time duration.</p>
                    </div>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.generatedMemes.map((meme, index) => {
            if (!meme.success) {
                return `
                    <div class="error-card">
                        <div class="error-content">
                            <h3>❌ Generation Failed</h3>
                            <p>${meme.error || 'Unknown error occurred'}</p>
                        </div>
                    </div>
                `;
            }

            const cleanBase64 = meme.png_base64.replace(/\s/g, '').trim();
            
            return `
                <div class="meme-card" onclick="window.memeUI.openMemeLink('${meme.url}')" title="Click to view source article">
                    <img src="data:image/png;base64,${cleanBase64}" 
                         alt="AI Generated Meme: ${(meme.prompt || 'Generated meme').substring(0, 100)}" 
                         class="meme-image"
                         loading="lazy"
                         onload="console.log('Image ${index + 1} loaded successfully'); this.classList.add('loaded')"
                         onerror="console.log('Image ${index + 1} failed to load'); this.parentElement.innerHTML='<div class=\\'error-card\\'><div class=\\'error-content\\'><h3>🖼️ Image Error</h3><p>Failed to load meme image</p></div></div>'">
                </div>
            `;
        }).join('');

        this.setupLazyLoading();
    }

    /**
     * Open meme source link
     * @param {string} url - URL to open
     */
    openMemeLink(url) {
        if (url && url !== 'https://example.com') {
            window.open(url, '_blank', 'noopener,noreferrer');
        }
    }

    /**
     * Show alert message
     * @param {string} message - Alert message
     * @param {string} type - Alert type (success, error, warning)
     */
    showAlert(message, type = 'success') {
        const alert = document.createElement('div');
        alert.className = `alert ${type}`;
        alert.textContent = message;
        document.body.appendChild(alert);
        
        setTimeout(() => alert.classList.add('show'), 100);
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    }

    /**
     * Show loading overlay
     */
    showLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.remove('hidden');
        }
    }

    /**
     * Hide loading overlay
     */
    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.add('hidden');
        }
        this.updateProgress(0, 'Ready to generate...', false);
    }

    /**
     * Update loading progress
     * @param {number} percent - Progress percentage
     * @param {string} text - Progress text
     * @param {boolean} animate - Whether to animate the progress
     */
    async updateProgress(percent, text, animate = true) {
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        const loadingText = document.getElementById('loadingText');
        
        if (progressFill) progressFill.style.width = percent + '%';
        if (progressText) progressText.textContent = percent + '% Complete';
        if (loadingText) loadingText.textContent = text;
        
        if (animate) {
            return this.sleep(200);
        }
    }

    /**
     * Handle keyboard shortcuts
     * @param {KeyboardEvent} e - Keyboard event
     */
    handleKeyboardShortcuts(e) {
        if (e.key.toLowerCase() === 'g' && this.selectedTrends.length > 0) {
            const isLoading = !document.getElementById('loadingOverlay').classList.contains('hidden');
            if (!isLoading) {
                this.handleGenerateMemes();
            }
        }
        
        if (e.key === 'Escape') {
            this.closeDropdown();
        }
        
        if (e.key === 'Backspace' && document.getElementById('memesPage').style.display === 'block') {
            e.preventDefault();
            this.goBack();
        }

        if (e.key === 'Enter' || e.key === ' ') {
            const activeElement = document.activeElement;
            if (activeElement && activeElement.classList.contains('dropdown-item')) {
                e.preventDefault();
                activeElement.click();
            }
        }
    }

    /**
     * Handle page visibility changes
     */
    handleVisibilityChange() {
        const spinners = document.querySelectorAll('.spinner');
        
        if (document.hidden) {
            spinners.forEach(spinner => {
                spinner.style.animationPlayState = 'paused';
            });
        } else {
            spinners.forEach(spinner => {
                spinner.style.animationPlayState = 'running';
            });
        }
    }

    /**
     * Setup touch support for mobile
     */
    setupTouchSupport() {
        let touchStartY = 0;
        
        document.addEventListener('touchstart', (e) => {
            touchStartY = e.touches[0].clientY;
        });

        document.addEventListener('touchend', (e) => {
            const touchEndY = e.changedTouches[0].clientY;
            const diff = touchStartY - touchEndY;
            
            if (diff > 100 && this.selectedTrends.length > 0) {
                const landingPageVisible = document.getElementById('landingPage').style.display !== 'none';
                if (landingPageVisible) {
                    this.handleGenerateMemes();
                }
            }
        });
    }

    /**
     * Setup accessibility features
     */
    setupAccessibility() {
        const dropdownButton = document.getElementById('dropdownButton');
        const dropdownMenu = document.getElementById('dropdownMenu');
        
        if (dropdownButton) {
            dropdownButton.setAttribute('aria-expanded', 'false');
            dropdownButton.setAttribute('aria-haspopup', 'listbox');
        }
        
        if (dropdownMenu) {
            dropdownMenu.setAttribute('role', 'listbox');
        }
        
        document.querySelectorAll('.dropdown-item').forEach(item => {
            item.setAttribute('role', 'option');
            item.setAttribute('tabindex', '0');
        });
    }

    /**
     * Setup lazy loading for images
     */
    setupLazyLoading() {
        const images = document.querySelectorAll('img[loading="lazy"]');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.classList.add('fade-in');
                        observer.unobserve(img);
                    }
                });
            });

            images.forEach(img => imageObserver.observe(img));
        }
    }

    /**
     * Setup Easter egg
     */
    setupEasterEgg() {
        let clickCount = 0;
        const header = document.querySelector('.header h1');
        
        if (header) {
            header.addEventListener('click', () => {
                clickCount++;
                if (clickCount === 5) {
                    this.showAlert('🎭 You found the Easter egg! You really love AI memes!', 'success');
                    clickCount = 0;
                }
            });
        }
    }

    /**
     * Track analytics events
     * @param {string} eventName - Event name
     * @param {Object} properties - Event properties
     */
    trackEvent(eventName, properties = {}) {
        console.log(`📊 Event: ${eventName}`, properties);
    }

    /**
     * Utility function for delays
     * @param {number} ms - Milliseconds to sleep
     * @returns {Promise} Promise that resolves after delay
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Initialize entrance animations
     */
    initializeAnimations() {
        setTimeout(() => {
            const header = document.querySelector('.header');
            const formContainer = document.querySelector('.form-container');
            
            if (header) {
                header.style.animation = 'fadeInUp 0.8s ease';
            }
            
            if (formContainer) {
                formContainer.style.animation = 'fadeInUp 0.8s ease 0.2s both';
            }
        }, 100);
    }
}

// Create global UI instance
console.log('🎨 Creating global memeUI instance...');
window.memeUI = new MemeUI();
console.log('✅ window.memeUI created:', window.memeUI);

// Export for module usage if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MemeUI;
}