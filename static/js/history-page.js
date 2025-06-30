/**
 * History page functionality for AI Meme Newsletter
 * Handles displaying and paginating previous meme generations
 */

class HistoryPage {
    constructor() {
        this.currentPage = 1;
        this.totalPages = 1;
        this.memesPerPage = 32;
        this.allMemes = [];
    }

    /**
     * Initialize the history page
     */
    init() {
        console.log('Initializing history page...');
        this.setupEventListeners();
        this.loadMemes();
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
            const data = await window.memeAPI.getMemes('recent', 0);
            
            if (data.success && data.memes) {
                this.allMemes = data.memes;
                console.log(`Loaded ${this.allMemes.length} memes`);
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
        const grid = document.getElementById('historyGrid');
        const startIdx = (this.currentPage - 1) * this.memesPerPage;
        const endIdx = startIdx + this.memesPerPage;
        const memesToShow = this.allMemes.slice(startIdx, endIdx);
        
        grid.innerHTML = '';
        
        memesToShow.forEach((meme, index) => {
            const card = this.createMemeCard(meme, startIdx + index);
            grid.appendChild(card);
        });
        
        this.updatePaginationControls();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    /**
     * Create a meme card with prompt display
     * 
     * @param {Object} meme - Meme data
     * @param {number} globalIndex - Index in the full array
     * @returns {HTMLElement} Meme card element
     */
    createMemeCard(meme, globalIndex) {
        const card = document.createElement('div');
        card.className = 'meme-card-container';
        
        const hasBase64 = meme.png_base64 && meme.png_base64.trim() !== '';
        const hasUrl = meme.url && meme.url.trim() !== '' && meme.url !== 'https://example.com';
        
        if (!hasBase64) {
            card.innerHTML = `
                <div class="meme-content">
                    <div class="error-card">
                        <div class="error-content">
                            <h3>Image Not Available</h3>
                            <p>This meme could not be loaded</p>
                        </div>
                    </div>
                </div>
            `;
            return card;
        }
        
        const imageSrc = `data:image/png;base64,${meme.png_base64}`;
        const timestamp = meme.generated_at || meme.timestamp;
        const formattedDate = timestamp ? this.formatDate(timestamp) : 'Unknown date';
        const trends = meme.trends_used ? meme.trends_used.join(', ') : 'Unknown trends';
        
        // Create clickable meme card
        const memeCardHTML = `
            <div class="meme-content" ${hasUrl ? `onclick="window.open('${meme.url}', '_blank')"` : ''}>
                <img 
                    src="${imageSrc}" 
                    alt="AI Meme #${globalIndex + 1}" 
                    class="meme-image"
                    onload="this.classList.add('loaded')"
                    onerror="this.parentElement.innerHTML='<div class=\\'error-card\\'><div class=\\'error-content\\'><h3>Failed to Load</h3><p>Image could not be displayed</p></div></div>'"
                >
                <div class="meme-info">
                    <div class="meme-prompt">
                        <strong>Prompt:</strong>
                        <p>${meme.prompt || 'No prompt available'}</p>
                    </div>
                    <div class="meme-metadata">
                        <span class="meme-date">${formattedDate}</span>
                        <span class="meme-trends">${trends}</span>
                    </div>
                </div>
            </div>
        `;
        
        card.innerHTML = memeCardHTML;
        return card;
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