"""
News fetching and aggregation using NewsAPI.

Setup:
    pip install newsapi-python python-dotenv
    
    Create .env file with:
    NEWS_API_KEY=your-newsapi-key-here
"""

from newsapi import NewsApiClient
import os
from datetime import datetime, timedelta
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure NewsAPI
api_key = os.getenv('NEWS_API_KEY')
if not api_key:
    raise ValueError("NEWS_API_KEY not found in .env file")

newsapi = NewsApiClient(api_key=api_key)


def get_news_articles(keywords: List[str], days_back: int = 1) -> List[Dict]:
    """
    Fetch recent news articles from NewsAPI.org.
    
    Args:
        keywords: List of keywords to search for in news articles
        days_back: Number of days to look back for news (default: 1)
        
    Returns:
        List of unique news articles sorted by importance
    """
    # Calculate date range
    to_date = datetime.now()
    from_date = to_date - timedelta(days=days_back)
    
    # Build query from keywords
    query = ' OR '.join(f'"{keyword}"' if ' ' in keyword else keyword for keyword in keywords)
    
    try:
        # Fetch by popularity
        popularity_response = newsapi.get_everything(
            q=query,
            from_param=from_date.strftime('%Y-%m-%d'),
            to=to_date.strftime('%Y-%m-%d'),
            sort_by='popularity',
            language='en',
            page_size=20,
        )
        
        # Fetch by relevance
        relevance_response = newsapi.get_everything(
            q=query,
            from_param=from_date.strftime('%Y-%m-%d'),
            to=to_date.strftime('%Y-%m-%d'),
            sort_by='relevancy',
            language='en',
            page_size=20,
        )
        
        # Extract articles
        popularity_articles = popularity_response.get('articles', [])
        relevance_articles = relevance_response.get('articles', [])
        
        print(f"📰 Found {len(popularity_articles)} popular and {len(relevance_articles)} relevant articles")
        
        # Combine and deduplicate
        combined_articles = merge_and_rank_articles(popularity_articles, relevance_articles)
        
        # Filter out invalid articles
        valid_articles = []
        for article in combined_articles:
            if is_valid_article(article):
                valid_articles.append(clean_article(article))
        
        print(f"✅ Returning {len(valid_articles)} valid articles")
        return valid_articles
        
    except Exception as e:
        print(f"❌ Error fetching news: {e}")
        return get_sample_articles()


def merge_and_rank_articles(popularity_articles: List[Dict], relevance_articles: List[Dict]) -> List[Dict]:
    """
    Merge articles from popularity and relevance searches, removing duplicates.
    Articles appearing in both lists get higher priority.
    
    Args:
        popularity_articles: Articles sorted by popularity
        relevance_articles: Articles sorted by relevance
        
    Returns:
        Combined list with duplicates removed, prioritizing overlap
    """
    # Create article maps with simplified titles as keys
    popularity_map = {simplify_title(a['title']): a for a in popularity_articles if a.get('title')}
    relevance_map = {simplify_title(a['title']): a for a in relevance_articles if a.get('title')}
    
    # Find articles that appear in both lists (highest priority)
    overlap_titles = set(popularity_map.keys()) & set(relevance_map.keys())
    
    # Create ranked list
    ranked_articles = []
    
    # 1. Add overlapping articles first (both popular AND relevant)
    for title in overlap_titles:
        ranked_articles.append(popularity_map[title])
    
    # 2. Add remaining popularity articles
    for title, article in popularity_map.items():
        if title not in overlap_titles:
            ranked_articles.append(article)
    
    # 3. Add remaining relevance articles
    for title, article in relevance_map.items():
        if title not in overlap_titles and title not in popularity_map:
            ranked_articles.append(article)
    
    return ranked_articles


def simplify_title(title: str) -> str:
    """
    Create simplified version of title for deduplication.
    
    Args:
        title: Original article title
        
    Returns:
        Simplified title (lowercase, no punctuation, first 50 chars)
    """
    if not title:
        return ""
    
    # Remove common punctuation and convert to lowercase
    simplified = title.lower()
    for char in ['.', ',', '!', '?', ':', ';', '-', '—', '"', "'", '(', ')']:
        simplified = simplified.replace(char, '')
    
    # Remove extra spaces and truncate
    simplified = ' '.join(simplified.split())
    return simplified[:50]


def is_valid_article(article: Dict) -> bool:
    """
    Check if article has required fields and is not removed content.
    
    Args:
        article: Article dictionary from NewsAPI
        
    Returns:
        True if article is valid, False otherwise
    """
    if not article.get('title') or not article.get('url'):
        return False
    
    if '[Removed]' in article.get('title', ''):
        return False
    
    if article.get('title', '').strip() == '':
        return False
    
    return True


def clean_article(article: Dict) -> Dict:
    """
    Clean and format article for output.
    
    Args:
        article: Raw article from NewsAPI
        
    Returns:
        Cleaned article dictionary
    """
    # Extract content, removing NewsAPI metadata
    content = article.get('content', '') or article.get('description', '')
    if content and '[+' in content:
        content = content.split('[+')[0].strip()
    
    return {
        "source": article.get('source', {}),
        "author": article.get('author', ''),
        "title": article.get('title', '').strip(),
        "description": article.get('description', '').strip() if article.get('description') else '',
        "url": article.get('url', ''),
        "urlToImage": article.get('urlToImage', ''),
        "publishedAt": article.get('publishedAt', ''),
        "content": content
    }


def get_sample_articles() -> List[Dict]:
    """
    Return sample articles for testing when API is unavailable.
    
    Returns:
        List of sample article dictionaries
    """
    return [
        {
            "source": {"id": "techcrunch", "name": "TechCrunch"},
            "author": "Sarah Chen",
            "title": "OpenAI Announces GPT-5 with Revolutionary Reasoning",
            "description": "The latest model demonstrates human-level problem solving.",
            "url": "https://example.com/gpt5",
            "urlToImage": "https://example.com/gpt5.jpg",
            "publishedAt": datetime.now().isoformat(),
            "content": "OpenAI unveiled GPT-5 today, claiming breakthrough capabilities..."
        },
        {
            "source": {"id": "the-verge", "name": "The Verge"},
            "author": "Mike Johnson",
            "title": "Google's Gemini Ultra Beats GPT-4 in Benchmarks",
            "description": "New benchmarks show Gemini outperforming competitors.",
            "url": "https://example.com/gemini",
            "urlToImage": "https://example.com/gemini.jpg",
            "publishedAt": (datetime.now() - timedelta(hours=2)).isoformat(),
            "content": "Google's Gemini Ultra has achieved state-of-the-art results..."
        }
    ]


# Example usage
if __name__ == "__main__":
    # Test with AI-related keywords
    keywords = ["artificial intelligence", "OpenAI", "ChatGPT", "machine learning"]
    
    articles = get_news_articles(keywords, days_back=1)
    
    print(f"\n📰 Retrieved {len(articles)} articles:")
    print("=" * 80)
    
    for i, article in enumerate(articles[:5], 1):  # Show first 5
        print(f"{i}. {article['title']}")
        print(f"   Source: {article['source']['name']}")
        print(f"   URL: {article['url']}")
        print("-" * 80)