async function generateMeme() {
    const generateBtn = document.getElementById('generate-btn');
    const overlay = document.getElementById('generating-overlay');
    
    if (!generateBtn || !overlay) {
        console.error('Required elements not found');
        return;
    }
    
    // Disable button and show overlay
    generateBtn.disabled = true;
    generateBtn.textContent = '🎲 Generating...';
    overlay.style.display = 'flex';
    
    // Animate steps
    const steps = ['step-1', 'step-2', 'step-3', 'step-4', 'step-5'];
    let currentStep = 0;
    
    const stepInterval = setInterval(() => {
        if (currentStep > 0) {
            const prevStep = document.getElementById(steps[currentStep - 1]);
            if (prevStep) {
                prevStep.classList.remove('active');
                prevStep.classList.add('completed');
            }
        }
        if (currentStep < steps.length) {
            const currentStepEl = document.getElementById(steps[currentStep]);
            if (currentStepEl) {
                currentStepEl.classList.add('active');
            }
            currentStep++;
        } else {
            clearInterval(stepInterval);
        }
    }, 1200);

    try {
        console.log('🎲 Starting meme generation...');
        
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('🎉 Fresh meme generated! Scroll down to see it.', 'success');
            
            // Reload page after a short delay to show the new meme
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            console.error('Meme generation failed:', data.error);
            showAlert('😅 Generation failed: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Generation error:', error);
        showAlert('🚨 Error generating meme. Please try again.', 'error');
    } finally {
        // Reset UI after delay
        setTimeout(() => {
            overlay.style.display = 'none';
            generateBtn.disabled = false;
            generateBtn.textContent = '🎲 Generate AI Meme';
            
            // Reset steps
            steps.forEach(stepId => {
                const step = document.getElementById(stepId);
                if (step) {
                    step.classList.remove('active', 'completed');
                }
            });
        }, 2000);
    }
}

async function voteMeme(memeId) {
    if (!memeId) {
        console.error('No meme ID provided');
        return;
    }
    
    if (votedMemes.has(memeId)) {
        showAlert('You already voted for this meme! 🗳️', 'info');
        return;
    }

    try {
        console.log('🗳️ Voting for meme:', memeId);
        
        const response = await fetch('/api/vote', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ meme_id: memeId })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update local storage
            votedMemes.add(memeId);
            localStorage.setItem('votedMemes', JSON.stringify([...votedMemes]));
            
            // Update button
            const btn = document.getElementById(`vote-${memeId}`);
            if (btn) {
                btn.classList.add('voted');
                btn.disabled = true;
                
                // Update vote count
                const currentVotes = parseInt(btn.textContent.match(/\d+/)?.[0] || 0);
                btn.textContent = `👍 ${currentVotes + 1}`;
            }
            
            showAlert('Vote counted! 👍', 'success');
            updateStats();
        } else {
            console.error('Vote failed:', data.message);
            showAlert(data.message || 'Could not vote', 'error');
        }
    } catch (error) {
        console.error('Voting error:', error);
        showAlert('Error voting. Please try again.', 'error');
    }
}

// Rate limiting for generation
let lastGenerationTime = 0;
const GENERATION_COOLDOWN = 10000; // 10 seconds

function canGenerate() {
    const now = Date.now();
    if (now - lastGenerationTime < GENERATION_COOLDOWN) {
        const remaining = Math.ceil((GENERATION_COOLDOWN - (now - lastGenerationTime)) / 1000);
        showAlert(`Please wait ${remaining} seconds before generating another meme`, 'info');
        return false;
    }
    lastGenerationTime = now;
    return true;
}

// Override the original generateMeme function to include rate limiting
const originalGenerateMeme = generateMeme;
generateMeme = function() {
    if (canGenerate()) {
        return originalGenerateMeme();
    }
};