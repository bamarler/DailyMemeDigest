"""
Database module for Neon PostgreSQL and Cloudinary storage
Maintains the same simple interface as the JSON version
"""

import os
import json
import base64
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
from contextlib import contextmanager
from typing import Dict, List
from datetime import datetime
import cloudinary
import cloudinary.uploader
from io import BytesIO
import uuid
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

try:
    connection_pool = psycopg2.pool.SimpleConnectionPool(
        1, 20,
        os.getenv('DATABASE_URL'),
        cursor_factory=RealDictCursor
    )
except Exception as e:
    print(f"Error creating connection pool: {e}")
    connection_pool = None

@contextmanager
def get_db_connection():
    """
    Context manager for database connections
    
    Yields:
        connection: Database connection from pool
    """
    if not connection_pool:
        raise Exception("Database connection pool not initialized")
    
    connection = connection_pool.getconn()
    try:
        yield connection
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        connection_pool.putconn(connection)

def save_meme(meme: Dict) -> str:
    """
    Save a single meme to database and upload image to Cloudinary
    
    Parameters:
        meme: Single meme generation result with required fields:
              - png_base64: base64 encoded image
              - prompt: meme generation prompt
              - url: news article URL
              - success: whether generation succeeded
              Optional fields:
              - timestamp or generated_at: when created
              - trends_used or trends: list of trends
              
    Returns:
        str: Cloudinary URL of saved meme, or empty string if failed
    """
    try:
        if not meme.get('success', True):
            print(f"Skipping failed meme: {meme.get('error', 'Unknown error')}")
            return ""
        
        base64_image = meme.get('png_base64', '')
        if not base64_image:
            print("No image data to upload")
            return ""
        
        if base64_image.startswith('data:'):
            base64_image = base64_image.split(',')[1]
        
        now = datetime.now()
        date_str = now.strftime('%Y/%m')
        public_id = f"memes/{date_str}/meme_{uuid.uuid4().hex[:8]}"
        
        image_bytes = base64.b64decode(base64_image)
        response = cloudinary.uploader.upload(
            BytesIO(image_bytes),
            public_id=public_id,
            folder="memes",
            format="webp",
            quality="auto:good",
            context={
                "prompt": meme.get('prompt', ''),
                "news_url": meme.get('url', ''),
                "created_at": meme.get('timestamp', meme.get('generated_at', now.isoformat()))
            },
            tags=meme.get('trends_used', meme.get('trends', []))
        )
        
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            timestamp_str = meme.get('timestamp', meme.get('generated_at', now.isoformat()))
            if isinstance(timestamp_str, str):
                created_at = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                created_at = now
            
            cur.execute("""
                INSERT INTO memes (
                    cloudinary_url, 
                    cloudinary_public_id, 
                    prompt, 
                    news_url, 
                    created_at
                )
                VALUES (%s, %s, %s, %s, %s)
            """, (
                response['secure_url'],
                response['public_id'],
                meme.get('prompt', ''),
                meme.get('url', ''),
                created_at
            ))
        
        print(f"✅ Saved meme to database and Cloudinary: {public_id}")
        return response['secure_url']
        
    except Exception as e:
        print(f"Warning: Could not save meme: {e}")
        return ""

def get_memes(sort_by: str = 'recent') -> List[Dict]:
    """
    Get memes from database
    
    Parameters:
        sort_by: How to sort ('recent' is the only option for now)
        
    Returns:
        List of meme dictionaries with Cloudinary URLs
    """
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            query = """
                SELECT 
                    id,
                    cloudinary_url,
                    prompt,
                    news_url,
                    created_at
                FROM memes
                ORDER BY created_at DESC
                LIMIT 200
            """
            
            cur.execute(query)
            memes = cur.fetchall()
            
            formatted_memes = []
            for meme in memes:
                formatted_memes.append({
                    'success': True,
                    'prompt': meme['prompt'],
                    'url': meme['news_url'],
                    'image': meme['cloudinary_url'],
                    'generated_at': meme['created_at'].isoformat()
                })
            
            return formatted_memes
            
    except Exception as e:
        print(f"Error getting memes: {e}")
        return []

def get_random_templates(count: int = 50) -> List[Dict]:
    """
    Get random meme templates from database
    
    Parameters:
        count: Number of templates to return
        
    Returns:
        List of template dictionaries
    """
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            cur.execute("""
                SELECT name, description, usage_context
                FROM templates
                WHERE description IS NOT NULL
                ORDER BY 
                    CASE 
                        WHEN popularity_score IS NOT NULL THEN popularity_score 
                        ELSE 0 
                    END DESC,
                    RANDOM()
                LIMIT %s
            """, (count,))
            
            templates = cur.fetchall()
            
            return [
                {
                    "meme": template['description'],
                    "usage_context": template['usage_context'] or ""
                }
                for template in templates
            ]
            
    except Exception as e:
        print(f"Error getting templates: {e}")
        return []