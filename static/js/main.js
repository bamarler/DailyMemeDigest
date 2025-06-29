// Global variables
let currentSort = 'recent';
let votedMemes = new Set(JSON.parse(localStorage.getItem('votedMemes') || '[]'));

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎭 AI Meme Factory initialized');
    
    loadNews();
    updateSortButtons();
    updateStats();
    markVotedMemes();
    
    // Auto-refresh news every 10 minutes
    setInterval(loadNews, 10 * 60 * 1000);
    
    // Auto-update stats every 30 seconds
    setInterval(updateStats, 30000);
});

// Utility Functions
function showAlert(message, type = 'success') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    document.body.appendChild(alert);
    
    setTimeout(() => alert.classList.add('show'), 100);
    setTimeout(() => {
        alert.classList.remove('show');
        setTimeout(() => alert.remove(), 300);
    }, 5000);
}

function updateSortButtons() {
    const urlParams = new URLSearchParams(window.location.search);
    const sort = urlParams.get('sort') || 'recent';
    currentSort = sort;
    
    document.getElementById('sort-recent')?.classList.toggle('active', sort === 'recent');
    document.getElementById('sort-popular')?.classList.toggle('active', sort === 'popular');
}

function markVotedMemes() {
    votedMemes.forEach(memeId => {
        const btn = document.getElementById(`vote-${memeId}`);
        if (btn) {
            btn.classList.add('voted');
            btn.disabled = true;
        }
    });
}

function updateStats() {
    const memeCards = document.querySelectorAll('.meme-card');
    const totalMemes = memeCards.length;
    
    let totalVotes = 0;
    memeCards.forEach(card => {
        const voteBtn = card.querySelector('.vote-btn');
        if (voteBtn) {
            const votes = parseInt(voteBtn.textContent.match(/\d+/)?.[0] || 0);
            totalVotes += votes;
        }
    });
    
    const totalMemesEl = document.getElementById('total-memes');
    const totalVotesEl = document.getElementById('total-votes');
    
    if (totalMemesEl) totalMemesEl.textContent = totalMemes;
    if (totalVotesEl) totalVotesEl.textContent = totalVotes;
}

// Sorting
function sortMemes(sortType) {
    const url = new URL(window.location);
    url.searchParams.set('sort', sortType);
    window.location.href = url.toString();
}

// Social Sharing
function shareToTwitter(memeId) {
    const text = encodeURIComponent("Check out this AI-generated meme from the latest tech news! 🤖🎭 #AI #memes #tech");
    const url = encodeURIComponent(window.location.origin + '/?meme=' + memeId);
    const twitterUrl = `https://twitter.com/intent/tweet?text=${text}&url=${url}`;
    window.open(twitterUrl, '_blank');
}

function copyMemeLink(memeId) {
    const url = window.location.origin + '/?meme=' + memeId;
    navigator.clipboard.writeText(url).then(() => {
        showAlert('Meme link copied to clipboard! 📋', 'success');
    }).catch(() => {
        showAlert('Could not copy link', 'error');
    });
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    showAlert('Something went wrong. Please refresh the page.', 'error');
});
