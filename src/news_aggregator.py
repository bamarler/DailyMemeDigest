# ==============================================================================
# FILE: src/news_aggregator.py
# News fetching and aggregation
# ==============================================================================

import requests
from datetime import datetime, timedelta
from typing import List
from .models import NewsItem
from .config import Config

class NewsAPIAggregator:
    """Professional AI news aggregation using NewsAPI.org"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = 'https://newsapi.org/v2'
        
        # Top tech sources for AI news
        self.ai_sources = [
            'techcrunch', 'the-verge', 'wired', 'ars-technica',
            'venturebeat', 'reuters', 'bbc-news', 'engadget',
            'mashable', 'recode'
        ]
        
        # AI keywords for targeted search
        self.ai_keywords = [
            'artificial intelligence', 'machine learning', 'OpenAI',
            'ChatGPT', 'Google AI', 'Meta AI', 'Anthropic', 'Claude',
            'GPT-4', 'GPT-5', 'neural network', 'deep learning',
            'autonomous', 'robotics', 'LLM', 'generative AI'
        ]
    
    def get_recent_news(self, hours_back: int = 24, max_articles: int = 15) -> List[NewsItem]:
        """Get recent AI news from major tech publications"""
        
        if self.api_key == 'your-news-api-key-here':
            # Fallback to sample data if no API key
            return self._get_sample_news()
        
        news_items = []
        
        # Calculate date range
        to_date = datetime.now()
        from_date = to_date - timedelta(hours=hours_back)
        
        try:
            # Search for AI-related articles
            url = f"{self.base_url}/everything"
            params = {
                'q': 'artificial intelligence OR OpenAI OR ChatGPT OR "machine learning" OR "AI model"',
                'sources': ','.join(self.ai_sources),
                'from': from_date.strftime('%Y-%m-%d'),
                'to': to_date.strftime('%Y-%m-%d'),
                'sortBy': 'publishedAt',
                'pageSize': max_articles,
                'language': 'en',
                'apiKey': self.api_key
            }
            
            print(f"🔍 Fetching AI news from NewsAPI...")
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                print(f"📰 Found {len(articles)} articles")
                
                for article in articles:
                    if article.get('title') and article.get('url'):
                        # Filter out removed/deleted articles
                        if '[Removed]' not in article.get('title', ''):
                            news_item = NewsItem(
                                title=article.get('title', '').strip(),
                                content=article.get('description', '')[:300] + '...' if article.get('description') else '',
                                url=article.get('url', ''),
                                source=article.get('source', {}).get('name', 'Unknown'),
                                published=article.get('publishedAt', '')
                            )
                            
                            news_items.append(news_item)
            
            elif response.status_code == 429:
                print("⚠️ NewsAPI rate limit exceeded, using sample data")
                return self._get_sample_news()
            
            else:
                print(f"❌ NewsAPI error: {response.status_code} - {response.text}")
                return self._get_sample_news()
                
        except Exception as e:
            print(f"❌ Error fetching news: {e}")
            return self._get_sample_news()
        
        # Remove duplicates and return
        unique_news = self._remove_duplicates(news_items)
        return unique_news[:max_articles]
    
    def _get_sample_news(self) -> List[NewsItem]:
        """Fallback sample news for demo purposes"""
        return [
            NewsItem(
                title="OpenAI Announces GPT-5 with Revolutionary Reasoning Capabilities",
                content="OpenAI today unveiled GPT-5, claiming it can solve complex mathematical proofs and write production-ready code with human-level accuracy.",
                url="https://example.com/gpt5",
                source="TechCrunch",
                published=(datetime.now() - timedelta(minutes=30)).isoformat()
            ),
            NewsItem(
                title="Google's Gemini Ultra Surpasses GPT-4 in Comprehensive AI Benchmarks",
                content="Google's latest AI model Gemini Ultra has achieved state-of-the-art results across multiple benchmarks, outperforming GPT-4 in reasoning and code generation.",
                url="https://example.com/gemini",
                source="The Verge",
                published=(datetime.now() - timedelta(hours=2)).isoformat()
            ),
            NewsItem(
                title="Meta Open Sources LLaMA 3 with 400B Parameters",
                content="Meta has released LLaMA 3, a massive 400 billion parameter language model that rivals proprietary alternatives and is available for commercial use.",
                url="https://example.com/llama3",
                source="VentureBeat",
                published=(datetime.now() - timedelta(hours=4)).isoformat()
            ),
            NewsItem(
                title="AI Coding Startup Raises $100M Series A for 'GitHub Copilot Killer'",
                content="CodeGenius, a startup building an AI coding assistant that generates entire applications, has raised $100M to compete with GitHub Copilot.",
                url="https://example.com/codegenius",
                source="TechCrunch",
                published=(datetime.now() - timedelta(hours=6)).isoformat()
            ),
            NewsItem(
                title="Anthropic's Claude 4 Demonstrates Human-Level Performance on Complex Reasoning",
                content="Anthropic's newest model Claude 4 shows human-level performance on complex reasoning tasks while maintaining strong safety properties.",
                url="https://example.com/claude4",
                source="Wired",
                published=(datetime.now() - timedelta(hours=8)).isoformat()
            ),
            NewsItem(
                title="Tesla's FSD Beta Achieves 99.9% Accuracy in Urban Driving Tests",
                content="Tesla's Full Self-Driving beta has reached a major milestone with 99.9% accuracy in complex urban driving scenarios across multiple cities.",
                url="https://example.com/tesla-fsd",
                source="Engadget",
                published=(datetime.now() - timedelta(hours=12)).isoformat()
            )
        ]
    
    def _remove_duplicates(self, news_items: List[NewsItem]) -> List[NewsItem]:
        """Remove duplicate articles based on title similarity"""
        unique_items = []
        seen_titles = set()
        
        for item in news_items:
            # Create simplified title for comparison
            simple_title = item.title.lower().replace(' ', '').replace('-', '')[:50]
            
            if simple_title not in seen_titles:
                seen_titles.add(simple_title)
                unique_items.append(item)
        
        return unique_items