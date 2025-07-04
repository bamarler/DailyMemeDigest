/**
 * Mosaic Grid Component
 * Reusable masonry-style grid layout for meme cards
 */

class MosaicGrid {
    /**
     * Create a mosaic grid instance
     * 
     * @param {string} containerId - ID of the container element
     * @param {Object} options - Configuration options
     */
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            baseColumnWidth: options.columnWidth || 250,
            gap: options.gap || 20,
            ...options
        };
        this.items = [];
        this.resizeTimeout = null;
        this.loadedImages = 0;
        
        this.init();
    }

    /**
     * Initialize the mosaic grid
     */
    init() {
        if (!this.container) {
            console.error('MosaicGrid: Container not found');
            return;
        }
        
        this.setupStyles();
        this.setupResizeListener();
    }

    /**
     * Setup grid styles
     */
    setupStyles() {
        this.container.style.position = 'relative';
        this.container.style.width = '100%';
    }

    /**
     * Setup window resize listener
     */
    setupResizeListener() {
        this.resizeListener = () => {
            clearTimeout(this.resizeTimeout);
            this.resizeTimeout = setTimeout(() => {
                this.reflow();
            }, 250);
        };
        
        window.addEventListener('resize', this.resizeListener);
    }

    /**
     * Calculate responsive column width
     */
    calculateColumnWidth() {
        const containerWidth = this.container.offsetWidth;
        const minColumns = Math.floor((containerWidth + this.options.gap) / (this.options.baseColumnWidth + this.options.gap));
        
        if (minColumns < 1) return this.options.baseColumnWidth;
        
        // Calculate actual column width to fill container
        const columnWidth = (containerWidth - (minColumns - 1) * this.options.gap) / minColumns;
        return columnWidth;
    }

    /**
     * Add items to the grid
     * 
     * @param {Array} memes - Array of meme objects
     * @param {Function} createCardFn - Function to create card HTML
     */
    addItems(memes, createCardFn) {
        this.container.innerHTML = '';
        this.items = [];
        this.loadedImages = 0;
        
        const columnWidth = this.calculateColumnWidth();
        
        memes.forEach((meme, index) => {
            const cardWrapper = document.createElement('div');
            cardWrapper.className = 'mosaic-item';
            cardWrapper.style.position = 'absolute';
            cardWrapper.innerHTML = createCardFn(meme, index);
            
            // Store data attributes
            cardWrapper.dataset.index = index;
            cardWrapper.dataset.columnSpan = 1; // Default
            
            this.container.appendChild(cardWrapper);
            this.items.push(cardWrapper);
            
            const img = cardWrapper.querySelector('.meme-card-image');
            if (img) {
                // Set initial size
                cardWrapper.style.width = columnWidth + 'px';
                cardWrapper.style.height = columnWidth + 'px';
                
                if (img.complete && img.naturalHeight > 0) {
                    this.handleImageLoad(img, cardWrapper);
                } else {
                    img.addEventListener('load', () => {
                        this.handleImageLoad(img, cardWrapper);
                    });
                    
                    img.addEventListener('error', () => {
                        console.error('Failed to load image:', img.src);
                        cardWrapper.style.width = columnWidth + 'px';
                        cardWrapper.style.height = columnWidth + 'px';
                        this.reflow();
                    });
                }
            } else {
                cardWrapper.style.width = columnWidth + 'px';
                cardWrapper.style.height = columnWidth + 'px';
            }
        });
        
        // Initial reflow
        this.reflow();
    }

    /**
     * Handle image load event
     * 
     * @param {HTMLImageElement} img - The loaded image
     * @param {HTMLElement} wrapper - The wrapper element
     */
    handleImageLoad(img, wrapper) {
        this.loadedImages++;
        
        if (img.naturalHeight > 0) {
            const aspectRatio = img.naturalWidth / img.naturalHeight;
            const columnWidth = this.calculateColumnWidth();
            const containerWidth = this.container.offsetWidth;
            const numColumns = Math.floor((containerWidth + this.options.gap) / (columnWidth + this.options.gap));
            
            // Determine column span based on aspect ratio
            let columnSpan = 1;
            if (aspectRatio > 1.7) {
                columnSpan = Math.min(2, numColumns);
            }
            if (aspectRatio > 2.5 && numColumns >= 3) {
                columnSpan = Math.min(3, numColumns);
            }
            
            wrapper.dataset.columnSpan = columnSpan;
            
            // Calculate width and height
            const itemWidth = (columnWidth * columnSpan) + (this.options.gap * (columnSpan - 1));
            const itemHeight = itemWidth / aspectRatio;
            
            wrapper.style.width = itemWidth + 'px';
            wrapper.style.height = itemHeight + 'px';
            
            const card = wrapper.querySelector('.meme-card');
            if (card) {
                card.style.height = itemHeight + 'px';
            }
        }
        
        this.reflow();
    }

    /**
     * Calculate grid layout and position items
     */
    reflow() {
        const containerWidth = this.container.offsetWidth;
        const columnWidth = this.calculateColumnWidth();
        const numColumns = Math.floor((containerWidth + this.options.gap) / (columnWidth + this.options.gap));
        
        if (numColumns < 1) return;
        
        // Track the height of each column
        const columnHeights = new Array(numColumns).fill(0);
        
        // Process items in their original order to maintain chronological sorting
        this.items.forEach(item => {
            const itemHeight = parseInt(item.style.height) || columnWidth;
            const columnSpan = parseInt(item.dataset.columnSpan) || 1;
            
            // Find the best position for this item
            let bestColumn = 0;
            let minHeight = Infinity;
            
            // Check each possible starting column
            for (let col = 0; col <= numColumns - columnSpan; col++) {
                // Get the maximum height across the columns this item would span
                let maxHeight = 0;
                for (let span = 0; span < columnSpan; span++) {
                    maxHeight = Math.max(maxHeight, columnHeights[col + span]);
                }
                
                if (maxHeight < minHeight) {
                    minHeight = maxHeight;
                    bestColumn = col;
                }
            }
            
            // Position the item
            const x = bestColumn * (columnWidth + this.options.gap);
            const y = minHeight;
            
            item.style.transform = `translate(${x}px, ${y}px)`;
            
            // Update column heights
            for (let span = 0; span < columnSpan; span++) {
                columnHeights[bestColumn + span] = minHeight + itemHeight + this.options.gap;
            }
        });
        
        // Set container height
        const maxHeight = Math.max(...columnHeights);
        this.container.style.height = maxHeight + 'px';
    }

    /**
     * Clear the grid
     */
    clear() {
        this.container.innerHTML = '';
        this.items = [];
        this.loadedImages = 0;
    }

    /**
     * Destroy the grid and cleanup
     */
    destroy() {
        this.clear();
        if (this.resizeListener) {
            window.removeEventListener('resize', this.resizeListener);
        }
    }
}

window.MosaicGrid = MosaicGrid;