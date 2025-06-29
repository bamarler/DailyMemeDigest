# ==============================================================================
# FILE: src/models.py
# Data models
# ==============================================================================

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class NewsItem:
    """Represents a news article"""
    title: str
    content: str
    url: str
    source: str
    published: str
    
    def to_dict(self) -> Dict[str, str]:
        return {
            'title': self.title,
            'content': self.content,
            'url': self.url,
            'source': self.source,
            'published': self.published
        }

@dataclass
class GeneratedMeme:
    """Represents a generated meme"""
    id: str
    template_name: str
    meme_text: Dict[str, Any]
    news_source: str
    created_at: str
    votes: int = 0
    image_data: Optional[str] = None
    news_title: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'template_name': self.template_name,
            'meme_text': self.meme_text,
            'news_source': self.news_source,
            'created_at': self.created_at,
            'votes': self.votes,
            'image_data': self.image_data,
            'news_title': self.news_title
        }

@dataclass
class MemeTemplate:
    """Represents a meme template configuration"""
    name: str
    description: str
    text_positions: List[Dict[str, Any]]
    generation_prompt: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'description': self.description,
            'text_positions': self.text_positions,
            'generation_prompt': self.generation_prompt
        }

@dataclass
class APIResponse:
    """Standard API response format"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        response = {'success': self.success}
        if self.data:
            response['data'] = self.data
        if self.error:
            response['error'] = self.error
        if self.message:
            response['message'] = self.message
        return response
