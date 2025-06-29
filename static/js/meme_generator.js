// Global variables to manage generation state
let isGenerating = false;
let lastGenerationTime = 0;
const COOLDOWN_PERIOD = 5000; // 5 seconds cooldown between generations

// DOM Elements
const generateBtn = document.getElementById('generate-btn');
const overlay = document.getElementById('generating-overlay');
const progressText = document.getElementById('progress-text');
const alertContainer = document.getElementById('alert-container');

// Show alert messages
function showAlert(message, type = 'info') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    
    alertContainer.appendChild(alert);
    
    // Remove alert after 5 seconds
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

// Display generated memes in the grid
function displayMemes(memes) {
    const memesContainer = document.getElementById('memes-container');
    memesContainer.innerHTML = ''; // Clear existing memes
    
    memes.forEach(meme => {
        const memeCard = document.createElement('div');
        memeCard.className = 'meme-card';
        
        // Create meme card HTML
        memeCard.innerHTML = `
            <img src="${meme.image_url}" class="meme-image" alt="Generated Meme">
            <div class="meme-info">
                <p class="meme-caption">${meme.caption || ''}</p>
                ${meme.news_title ? `<p class="news-title">Based on: ${meme.news_title}</p>` : ''}
            </div>
        `;
        
        // Add click handler for saving/sharing if needed
        memeCard.addEventListener('click', () => {
            // Handle meme click - could be used for expanding view, sharing, etc.
        });
        
        memesContainer.appendChild(memeCard);
    });
}

// Check if enough time has passed since last generation
function checkCooldown() {
    const now = Date.now();
    const timeElapsed = now - lastGenerationTime;
    return timeElapsed >= COOLDOWN_PERIOD;
}

// Update UI to show generation progress
function updateProgress(message) {
    if (progressText) {
        progressText.textContent = message;
    }
}

// Main generation function
async function generateMeme() {
    // Prevent multiple simultaneous generations
    if (isGenerating) {
        showAlert('Please wait, already generating memes...', 'warning');
        return;
    }

    // Check cooldown period
    if (!checkCooldown()) {
        const remainingTime = Math.ceil((COOLDOWN_PERIOD - (Date.now() - lastGenerationTime)) / 1000);
        showAlert(`Please wait ${remainingTime} seconds before generating again`, 'warning');
        return;
    }

    try {
        // Update UI state
        isGenerating = true;
        generateBtn.disabled = true;
        generateBtn.textContent = 'Generating...';
        overlay.classList.remove('hidden');
        updateProgress('Gathering latest AI news...');

        // Make API call to backend
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
            // Add any necessary body data here if needed
            // body: JSON.stringify({ ... })
        });

        const data = await response.json();

        if (data.success) {
            // Show success message with generation stats
            showAlert(
                `🎉 Successfully generated ${data.successful_count} out of ${data.total_count} memes!`, 
                'success'
            );
            
            // Display the generated memes
            displayMemes(data.memes);
        } else {
            // Handle generation failure
            showAlert(data.error || 'Failed to generate memes', 'error');
        }

    } catch (error) {
        console.error('Meme generation error:', error);
        showAlert('Failed to generate memes. Please try again later.', 'error');
    } finally {
        // Reset UI state
        isGenerating = false;
        generateBtn.disabled = false;
        generateBtn.textContent = 'Generate Meme';
        overlay.classList.add('hidden');
        lastGenerationTime = Date.now();
    }
}

// Initialize event listeners
function initializeMemeGenerator() {
    // Add click handler to generate button
    if (generateBtn) {
        generateBtn.addEventListener('click', generateMeme);
    }

    // Optional: Add keyboard shortcut (e.g., press 'G' to generate)
    document.addEventListener('keydown', (e) => {
        if (e.key.toLowerCase() === 'g' && !isGenerating && checkCooldown()) {
            generateMeme();
        }
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeMemeGenerator);

// Export functions if needed for testing or external use
export {
    generateMeme,
    displayMemes,
    showAlert,
    checkCooldown
};