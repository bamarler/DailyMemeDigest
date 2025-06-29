// Global variables for tracking generation state
let lastGenerationTime = 0;
const COOLDOWN_PERIOD = 10000; // 10 seconds cooldown between generations
let isGenerating = false;

// Progress steps for generation animation
const PROGRESS_STEPS = [
    'Finding trending AI news...',
    'Analyzing content...',
    'Crafting meme concept...',
    'Generating image...',
    'Adding finishing touches...'
];

async function generateMeme() {
    // Prevent multiple simultaneous generations
    if (isGenerating) {
        return;
    }

    // Check cooldown period
    const now = Date.now();
    if (now - lastGenerationTime < COOLDOWN_PERIOD) {
        const remainingTime = Math.ceil((COOLDOWN_PERIOD - (now - lastGenerationTime)) / 1000);
        showAlert(`Please wait ${remainingTime} seconds before generating another meme`, 'warning');
        return;
    }

    const generateBtn = document.getElementById('generate-btn');
    const overlay = document.getElementById('generating-overlay');
    const progressText = document.getElementById('progress-text');
    
    try {
        // Set generation state
        isGenerating = true;
        generateBtn.disabled = true;
        generateBtn.textContent = 'Generating...';
        overlay.classList.remove('hidden');

        // Start progress animation
        startProgressAnimation(progressText);

        // Make API call to generate meme
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                // Add any parameters needed by your backend
                timestamp: new Date().toISOString()
            })
        });

        const data = await response.json();

        if (data.success) {
            showAlert('🎉 Fresh meme generated!', 'success');
            // Reload page after 2 seconds to show new meme
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            showAlert(data.error || 'Failed to generate meme', 'error');
        }

    } catch (error) {
        console.error('Generation error:', error);
        showAlert('Failed to generate meme. Please try again.', 'error');
    } finally {
        // Reset UI state
        isGenerating = false;
        generateBtn.disabled = false;
        generateBtn.textContent = 'Generate Meme';
        overlay.classList.add('hidden');
        lastGenerationTime = Date.now();
    }
}

// Progress animation function
function startProgressAnimation(progressText) {
    let currentStep = 0;
    
    const updateProgress = () => {
        if (currentStep < PROGRESS_STEPS.length && isGenerating) {
            progressText.textContent = PROGRESS_STEPS[currentStep];
            currentStep++;
            setTimeout(updateProgress, 1500); // Update every 1.5 seconds
        }
    };

    updateProgress();
}

// Alert function for user feedback
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) {
        // Create alert container if it doesn't exist
        const container = document.createElement('div');
        container.id = 'alert-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
        `;
        document.body.appendChild(container);
    }

    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    alert.style.cssText = `
        padding: 15px;
        margin-bottom: 10px;
        border-radius: 4px;
        opacity: 0;
        transition: opacity 0.3s ease-in;
    `;

    // Style based on alert type
    switch(type) {
        case 'success':
            alert.style.backgroundColor = '#d4edda';
            alert.style.color = '#155724';
            break;
        case 'error':
            alert.style.backgroundColor = '#f8d7da';
            alert.style.color = '#721c24';
            break;
        case 'warning':
            alert.style.backgroundColor = '#fff3cd';
            alert.style.color = '#856404';
            break;
        default:
            alert.style.backgroundColor = '#d1ecf1';
            alert.style.color = '#0c5460';
    }

    alertContainer.appendChild(alert);
    
    // Fade in
    setTimeout(() => {
        alert.style.opacity = '1';
    }, 10);

    // Remove alert after 3 seconds
    setTimeout(() => {
        alert.style.opacity = '0';
        setTimeout(() => {
            alertContainer.removeChild(alert);
        }, 300);
    }, 3000);
}

// Event listener for generate button
document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generate-btn');
    if (generateBtn) {
        generateBtn.addEventListener('click', generateMeme);
    }
});

// Export functions if needed
export {
    generateMeme,
    showAlert
};