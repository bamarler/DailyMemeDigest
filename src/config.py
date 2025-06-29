# ==============================================================================
# FILE: src/config.py
# Configuration settings
# ==============================================================================

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    NEWS_API_KEY = os.getenv('NEWS_API_KEY', 'your-news-api-key-here')
    
    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'memes.db')
    
    # Meme Generation Settings
    MAX_MEMES_PER_USER = int(os.getenv('MAX_MEMES_PER_USER', '10'))
    MEME_GENERATION_TIMEOUT = int(os.getenv('MEME_GENERATION_TIMEOUT', '60'))
    
    # News Settings
    NEWS_REFRESH_INTERVAL = int(os.getenv('NEWS_REFRESH_INTERVAL', '3600'))  # 1 hour
    MAX_NEWS_ARTICLES = int(os.getenv('MAX_NEWS_ARTICLES', '20'))
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', '10'))
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        errors = []
        
        if cls.OPENAI_API_KEY == 'your-openai-key-here':
            errors.append("OPENAI_API_KEY not configured")
        
        if cls.NEWS_API_KEY == 'your-news-api-key-here':
            print("⚠️ NEWS_API_KEY not configured - will use sample data")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True