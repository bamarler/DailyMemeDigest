# ==============================================================================
# FILE: src/utils.py
# Utility functions
# ==============================================================================

import re
import hashlib
from datetime import datetime
from typing import Any, Dict, List

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters that might break JSON
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    
    return text

def truncate_text(text: str, max_length: int) -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    
    # Try to cut at word boundary
    if ' ' in text[:max_length]:
        return text[:text.rfind(' ', 0, max_length)] + '...'
    else:
        return text[:max_length-3] + '...'

def generate_hash(text: str) -> str:
    """Generate hash for text deduplication"""
    return hashlib.md5(text.encode()).hexdigest()

def format_time_ago(timestamp: str) -> str:
    """Format timestamp as 'time ago' string"""
    try:
        if 'T' in timestamp:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        else:
            dt = datetime.fromisoformat(timestamp)
        
        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        diff = now - dt
        
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return "Just now"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif seconds < 86400:
            hours = int(seconds // 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        else:
            days = int(seconds // 86400)
            return f"{days} day{'s' if days != 1 else ''} ago"
            
    except Exception:
        return "Recently"

def validate_meme_text(meme_text: Dict[str, Any], template_name: str) -> bool:
    """Validate meme text structure for template"""
    
    required_fields = {
        "drake_pointing": ["top_text", "bottom_text"],
        "expanding_brain": ["level1", "level2", "level3", "level4"],
        "distracted_boyfriend": ["girlfriend", "boyfriend", "distraction"],
        "this_is_fine": ["caption"],
        "two_buttons": ["button1", "button2", "caption"],
        "woman_yelling_at_cat": ["woman", "cat"]
    }
    
    required = required_fields.get(template_name, [])
    
    for field in required:
        if field not in meme_text or not meme_text[field]:
            return False
    
    return True

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove or replace unsafe characters
    filename = re.sub(r'[^\w\s-]', '', filename)
    filename = re.sub(r'[-\s]+', '-', filename)
    return filename.strip('-')

class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, max_calls: int, time_window: int):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = {}
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if identifier is within rate limits"""
        now = datetime.now()
        
        if identifier not in self.calls:
            self.calls[identifier] = []
        
        # Remove old calls outside time window
        self.calls[identifier] = [
            call_time for call_time in self.calls[identifier]
            if (now - call_time).total_seconds() < self.time_window
        ]
        
        # Check if under limit
        if len(self.calls[identifier]) < self.max_calls:
            self.calls[identifier].append(now)
            return True
        
        return False

