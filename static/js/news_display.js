async function loadNews() {
    const container = document.getElementById('news-container');
    if (!container) return;
    
    try {
        console.log('📰 Loading news...');
        
        const response = await fetch('/api/news');
        const data = await response.json();
        
        if (data.news && data.news.length > 0) {
            displayNews(data.news);
        } else {
            container.innerHTML = '<p style="text-align: center; color: #666;">No recent AI news available</p>';
        }
    } catch (error) {
        console.error('Error loading news:', error);
        container.innerHTML = '<p style="text-align: center; color: #666;">Error loading news</p>';
    }
}

function displayNews(newsItems) {
    const container = document.getElementById('news-container');
    if (!container) return;
    
    container.innerHTML = newsItems.map((item, index) => {
        const timeAgo = getTimeAgo(item.published);
        return `
            <div class="news-ticker" onclick="openNewsLink('${item.url}')" title="Click to read full article">
                <div class="news-item-title">${escapeHtml(item.title)}</div>
                <div class="news-meta">
                    <span class="news-source">${escapeHtml(item.source)}</span>
                    <span class="news-time">${timeAgo}</span>
                </div>
            </div>
        `;
    }).join('');
}

function getTimeAgo(published) {
    try {
        const now = new Date();
        const pubDate = new Date(published);
        const diffMs = now - pubDate;
        const diffMins = Math.floor(diffMs / (1000 * 60));
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        
        if (diffHours > 24) {
            const diffDays = Math.floor(diffHours / 24);
            return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
        } else if (diffHours > 0) {
            return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        } else if (diffMins > 0) {
            return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
        } else {
            return 'Just now';
        }
    } catch (e) {
        console.error('Error parsing date:', e);
        return 'Recently';
    }
}

function openNewsLink(url) {
    if (url && url !== 'https://example.com') {
        window.open(url, '_blank', 'noopener,noreferrer');
    }
}

async function refreshNews() {
    const container = document.getElementById('news-container');
    if (!container) return;
    
    container.innerHTML = '<div class="loading"><div class="spinner"></div><p>Refreshing news...</p></div>';
    
    try {
        await loadNews();
        showAlert('📰 News refreshed!', 'info');
    } catch (error) {
        console.error('Error refreshing news:', error);
        showAlert('Error refreshing news', 'error');
    }
}

// Utility function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Auto-refresh news periodically
setInterval(() => {
    console.log('🔄 Auto-refreshing news...');
    loadNews();
}, 15 * 60 * 1000); // Every 15 minutes