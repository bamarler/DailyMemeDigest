/**
 * History page functionality for Daily Meme Digest
 * Handles displaying and paginating previous meme generations
 */

class HistoryPage {
    constructor() {
        this.currentPage = 1;
        this.totalPages = 1;
        this.memesPerPage = 32;
        this.allMemes = [];
        this.mosaicGrid = null;
    }

    /**
     * Initialize the history page
     */
    init() {
        console.log('Initializing history page...');
        this.setupEventListeners();
        this.initializeMosaicGrid();
        this.loadMemes();
    }

    /**
     * Initialize the mosaic grid
     */
    initializeMosaicGrid() {
        this.mosaicGrid = new MosaicGrid('historyGrid', {
            columnWidth: 250,
            gap: 20
        });
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        const prevBtn = document.getElementById('prevPageBtn');
        const nextBtn = document.getElementById('nextPageBtn');
        
        if (prevBtn) {
            prevBtn.addEventListener('click', () => this.changePage(-1));
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', () => this.changePage(1));
        }
    }

    /**
     * Load memes from the API
     */
    async loadMemes() {
        const grid = document.getElementById('historyGrid');
        this.showLoading();
        
        try {
            const data = await window.memeAPI.getMemes();
            
            if (data.success && data.memes) {
                this.allMemes = data.memes.sort((a, b) => {
                    const dateA = new Date(a.generated_at || a.timestamp);
                    const dateB = new Date(b.generated_at || b.timestamp);
                    return dateB - dateA;
                });
                console.log(`Loaded ${this.allMemes.length} memes, sorted by date`);
            } else {
                console.error('Invalid response:', data);
                this.allMemes = [];
            }
        } catch (error) {
            console.error('Error loading memes:', error);
            this.showAlert('Failed to load memes', 'error');
            this.allMemes = [];
        } finally {
            this.hideLoading();
        }
        
        if (this.allMemes.length === 0) {
            grid.innerHTML = `
                <div class="empty-state">
                    <h3>No Previous Memes</h3>
                    <p>Generate some memes first to see them here!</p>
                    <a href="/" class="generate-link">Go Generate Some Memes!</a>
                </div>
            `;
            this.updatePaginationControls();
            return;
        }
        
        this.totalPages = Math.ceil(this.allMemes.length / this.memesPerPage);
        this.currentPage = 1;
        this.displayCurrentPage();
    }

    /**
     * Display memes for the current page
     */
    displayCurrentPage() {
        const startIdx = (this.currentPage - 1) * this.memesPerPage;
        const endIdx = startIdx + this.memesPerPage;
        const memesToShow = this.allMemes.slice(startIdx, endIdx);
        
        this.mosaicGrid.addItems(memesToShow, (meme, index) => {
            return this.createMemeCard(meme, startIdx + index);
        });
        
        this.updatePaginationControls();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    /**
     * Create a meme card with unified design
     * 
     * @param {Object} meme - Meme data
     * @param {number} globalIndex - Index in the full array
     * @returns {string} HTML string for meme card
     */
    createMemeCard(meme, globalIndex) {
        const hasImage = meme.image && meme.image.trim() !== '';
        const hasUrl = meme.url && meme.url.trim() !== '' && meme.url !== 'https://example.com';
        
        if (!hasImage) {
            return `
                <div class="meme-card-wrapper">
                    <div class="meme-card-error">
                        <div class="meme-error-content">
                            <h3>Image Not Available</h3>
                            <p>This meme could not be loaded</p>
                        </div>
                    </div>
                </div>
            `;
        }
        
        const timestamp = meme.generated_at || meme.timestamp;
        const formattedDate = timestamp ? this.formatDate(timestamp) : 'Unknown date';
        const trends = meme.trends_used || meme.trends || [];
        const trendsText = Array.isArray(trends) ? trends.join(', ') : 'Unknown trends';
        
        const clickHandler = hasUrl ? `onclick="window.open('${meme.url}', '_blank')"` : '';
        
        return `
            <div class="meme-card-wrapper" ${clickHandler}>
                <div class="meme-card">
                    <div class="meme-card-face meme-card-front">
                        <img 
                            src="${meme.image}" 
                            alt="AI Meme #${globalIndex + 1}" 
                            class="meme-card-image"
                            loading="lazy"
                            onerror="this.parentElement.parentElement.innerHTML='<div class=\\'meme-card-error\\'><div class=\\'meme-error-content\\'><h3>Failed to Load</h3><p>Image could not be displayed</p></div></div>'"
                        >
                    </div>
                    <div class="meme-card-face meme-card-back">
                        <div class="meme-card-back-content">
                            <div class="meme-prompt-section">
                                <div class="meme-prompt-label">Prompt</div>
                                <div class="meme-prompt-text">${meme.prompt || 'No prompt available'}</div>
                                ${trends.length > 0 ? `
                                    <div class="meme-prompt-label" style="margin-top: 15px;">Trends Used</div>
                                    <div class="meme-prompt-text" style="font-size: 0.8rem;">${trendsText}</div>
                                ` : ''}
                            </div>
                            <div class="meme-metadata-section">
                                <div class="meme-timestamp">Generated: ${formattedDate}</div>
                                ${hasUrl ? '<div class="meme-url-hint">Click to view source article</div>' : ''}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Format date for display
     * 
     * @param {string} timestamp - ISO timestamp
     * @returns {string} Formatted date
     */
    formatDate(timestamp) {
        try {
            const date = new Date(timestamp);
            const options = { 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            };
            return date.toLocaleDateString('en-US', options);
        } catch (error) {
            return 'Unknown date';
        }
    }

    /**
     * Change page
     * 
     * @param {number} direction - Direction to change (-1 or 1)
     */
    changePage(direction) {
        const newPage = this.currentPage + direction;
        
        if (newPage >= 1 && newPage <= this.totalPages) {
            this.currentPage = newPage;
            this.displayCurrentPage();
        }
    }

    /**
     * Update pagination controls
     */
    updatePaginationControls() {
        const prevBtn = document.getElementById('prevPageBtn');
        const nextBtn = document.getElementById('nextPageBtn');
        const pageInfo = document.getElementById('pageInfo');
        const pagination = document.getElementById('pagination');
        
        if (this.allMemes.length === 0) {
            pagination.style.display = 'none';
            return;
        }
        
        pagination.style.display = 'flex';
        
        prevBtn.disabled = this.currentPage === 1;
        nextBtn.disabled = this.currentPage === this.totalPages;
        
        pageInfo.textContent = `Page ${this.currentPage} of ${this.totalPages}`;
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
    }

    /**
     * Show alert message
     * 
     * @param {string} message - Alert message
     * @param {string} type - Alert type
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
}

// Create global instance
window.historyPage = new HistoryPage();