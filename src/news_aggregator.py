# ==============================================================================
# FILE: src/news_aggregator.py
# News fetching and aggregation
# ==============================================================================

import requests
import os
from datetime import datetime, timedelta
from typing import List

# Handle imports for both direct execution and module import
try:
    from .models import NewsItem
    from .config import Config
except ImportError:
    from models import NewsItem
    from config import Config

class NewsAPIAggregator:
    """Professional AI news aggregation using NewsAPI.org"""
    
    def __init__(self, api_key: str):
        """
        Initialize the NewsAPIAggregator with API credentials and configuration.
        
        Input:
            api_key (str): NewsAPI.org API key for authentication
            
        Output:
            None (initializes the aggregator instance)
        """
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
    
    def get_recent_news(self, hours_back: int = 24) -> List[NewsItem]:
        """
        Fetch recent AI-related news articles from NewsAPI.org.
        
        Makes two API requests - one sorted by popularity and one by relevance,
        then combines and deduplicates the results.
        
        Input:
            hours_back (int): Number of hours to look back for news (default: 24)
            
        Output:
            List[NewsItem]: List of unique news articles with title, content, URL, source, and published date
        """
        
        if self.api_key == 'your-news-api-key-here':
            # Fallback to sample data if no API key
            return self._get_sample_news()
        
        news_items = []
        
        # Calculate date range
        to_date = datetime.now()
        from_date = to_date - timedelta(hours=hours_back)
        
        try:
            # Search for AI-related articles using /everything endpoint
            url = f"{self.base_url}/everything"
            
            # First, try a simple query without date restrictions
            simple_params = {
                'q': 'AI',
                'sortBy': 'popularity',
                'pageSize': 5,
                'language': 'en',
                'apiKey': self.api_key
            }
            
            print(f"🔍 Testing simple query first...")
            simple_response = requests.get(url, params=simple_params, timeout=15)
            print(f"📊 Simple query status: {simple_response.status_code}")
            if simple_response.status_code == 200:
                simple_data = simple_response.json()
                print(f"📊 Simple query found {len(simple_data.get('articles', []))} articles")
            else:
                print(f"❌ Simple query error: {simple_response.text}")
            
            popularity_params = {
                'q': 'artificial intelligence OR OpenAI OR ChatGPT OR "machine learning" OR "AI model"',
                'from': from_date.strftime('%Y-%m-%d'),
                'to': to_date.strftime('%Y-%m-%d'),
                'sortBy': 'popularity',
                'pageSize': 15,
                'language': 'en',
                'apiKey': self.api_key
            }

            relevance_params = {
                'q': 'artificial intelligence OR OpenAI OR ChatGPT OR "machine learning" OR "AI model"',
                'from': from_date.strftime('%Y-%m-%d'),
                'to': to_date.strftime('%Y-%m-%d'),
                'sortBy': 'relevance',
                'pageSize': 15,
                'language': 'en',
                'apiKey': self.api_key
            }
            
            print(f"🔍 Fetching AI news from NewsAPI...")
            popularity_response = requests.get(url, params=popularity_params, timeout=15)
            relevance_response = requests.get(url, params=relevance_params, timeout=15)
            
            # Debug: Print response details
            print(f"📊 Popularity response status: {popularity_response.status_code}")
            print(f"📊 Relevance response status: {relevance_response.status_code}")
            
            if popularity_response.status_code == 200:
                popularity_data = popularity_response.json()
                print(f"📊 Popularity response: {popularity_data}")
            else:
                print(f"❌ Popularity response error: {popularity_response.text}")
                
            if relevance_response.status_code == 200:
                relevance_data = relevance_response.json()
                print(f"📊 Relevance response: {relevance_data}")
            else:
                print(f"❌ Relevance response error: {relevance_response.text}")
            
            # Check both responses for errors
            if popularity_response.status_code == 429 or relevance_response.status_code == 429:
                print("⚠️ NewsAPI rate limit exceeded, using sample data")
                return self._get_sample_news()
            
            if popularity_response.status_code != 200 or relevance_response.status_code != 200:
                print(f"❌ NewsAPI error: Popularity {popularity_response.status_code}, Relevance {relevance_response.status_code}")
                return self._get_sample_news()
            
            # Process both responses
            popularity_data = popularity_response.json()
            relevance_data = relevance_response.json()
            
            popularity_articles = popularity_data.get('articles', [])
            relevance_articles = relevance_data.get('articles', [])
            
            # Combine articles from both responses
            all_articles = popularity_articles + relevance_articles
            
            print(f"📰 Found {len(popularity_articles)} popular articles and {len(relevance_articles)} relevant articles")
            
            # Debug: Check if articles have required fields
            valid_articles = 0
            filtered_articles = 0
            for i, article in enumerate(all_articles):
                print(f"🔍 Processing article {i+1}: {article.get('title', 'NO TITLE')[:50]}...")
                
                if not article.get('title'):
                    print(f"   ❌ Filtered out: No title")
                    filtered_articles += 1
                    continue
                    
                if not article.get('url'):
                    print(f"   ❌ Filtered out: No URL")
                    filtered_articles += 1
                    continue
                    
                if '[Removed]' in article.get('title', ''):
                    print(f"   ❌ Filtered out: Contains [Removed]")
                    filtered_articles += 1
                    continue
                
                print(f"   ✅ Valid article")
                valid_articles += 1
                news_item = NewsItem(
                    title=article.get('title', '').strip(),
                    content=article.get('description', '')[:300] + '...' if article.get('description') else '',
                    url=article.get('url', ''),
                    source=article.get('source', {}).get('name', 'Unknown'),
                    published=article.get('publishedAt', '')
                )
                
                news_items.append(news_item)
            
            print(f"🔍 Valid articles after filtering: {valid_articles}")
            print(f"🔍 Filtered out articles: {filtered_articles}")
            
        except Exception as e:
            print(f"❌ Error fetching news: {e}")
            return self._get_sample_news()
        
        # Remove duplicates and return
        unique_news = self._remove_duplicates(news_items)
        return unique_news
    
    def _get_sample_news(self) -> List[NewsItem]:
        """
        Generate sample news articles for demonstration and fallback purposes.
        
        Used when NewsAPI is unavailable, rate limited, or no API key is provided.
        Creates realistic AI-related news items with proper formatting.
        
        Input:
            None
            
        Output:
            List[NewsItem]: List of 6 sample AI news articles with mock data
        """
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
        """
        Remove duplicate news articles based on title similarity.
        
        Compares simplified versions of titles (lowercase, no spaces, no hyphens)
        to identify and remove duplicate articles from the combined list.
        
        Input:
            news_items (List[NewsItem]): List of news articles that may contain duplicates
            
        Output:
            List[NewsItem]: List of unique news articles with duplicates removed
        """
        unique_items = []
        seen_titles = set()
        
        for item in news_items:
            # Create simplified title for comparison
            simple_title = item.title.lower().replace(' ', '').replace('-', '')[:50]
            
            if simple_title not in seen_titles:
                seen_titles.add(simple_title)
                unique_items.append(item)
        
        return unique_items


def main():
    """
    Test function for NewsAPIAggregator functionality.
    
    Demonstrates the news aggregation process by fetching AI-related news,
    displaying the results in a formatted output, and showing debugging information.
    Uses environment variable NEWS_API_KEY for authentication.
    
    Input:
        None (reads from environment variables)
        
    Output:
        None (prints formatted news articles to console)
    """
    print("🤖 Testing NewsAPIAggregator...")
    
    # Get API key from environment
    api_key = os.getenv('NEWS_API_KEY')
    print(f"🔑 Using API key: {api_key[:10] + '...' if api_key and len(api_key) > 10 else 'None/Invalid'}")
    
    # Initialize with API key
    aggregator = NewsAPIAggregator(api_key=api_key)
    
    # Get recent news
    news_items = aggregator.get_recent_news(hours_back=24)
    
    print(f"\n📰 Retrieved {len(news_items)} news items:")
    print("=" * 80)
    
    for i, item in enumerate(news_items, 1):
        print(f"{i}. {item.title}")
        print(f"   Source: {item.source}")
        print(f"   Published: {item.published}")
        print(f"   URL: {item.url}")
        print(f"   Content: {item.content[:100]}...")
        print("-" * 80)
    
    print("\n✅ Test completed!")


if __name__ == "__main__":
    main()