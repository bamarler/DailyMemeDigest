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
              - template_id: UUID of template used
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
        
        # Try Cloudinary upload
        try:
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
                    "created_at": meme.get('timestamp', meme.get('generated_at', now.isoformat())),
                    "template_id": str(meme.get('template_id', ''))
                },
                tags=meme.get('trends_used', meme.get('trends', []))
            )
            cloudinary_url = response['secure_url']
            cloudinary_public_id = response['public_id']
        except Exception as cloud_error:
            print(f"Cloudinary upload failed: {cloud_error}")
            # Fallback to local storage
            cloudinary_url = f"local://memes/{public_id}"
            cloudinary_public_id = public_id
            save_meme_locally(meme)
        
        # Try database save
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                
                timestamp_str = meme.get('timestamp', meme.get('generated_at', now.isoformat()))
                if isinstance(timestamp_str, str):
                    created_at = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                else:
                    created_at = now
                
                # Get template_id - handle both string and None
                template_id = meme.get('template_id')
                if template_id and isinstance(template_id, str) and template_id.startswith('local_'):
                    template_id = None  # Don't save local IDs to database
                
                cur.execute("""
                    INSERT INTO memes (
                        cloudinary_url, 
                        cloudinary_public_id, 
                        prompt, 
                        news_url, 
                        created_at,
                        template_id
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    cloudinary_url,
                    cloudinary_public_id,
                    meme.get('prompt', ''),
                    meme.get('url', ''),
                    created_at,
                    template_id
                ))
            
            print(f"✅ Saved meme to database and Cloudinary: {public_id}")
        except Exception as db_error:
            print(f"Database save failed: {db_error}")
            # Fallback to local JSON
            save_meme_locally(meme)
        
        return cloudinary_url
        
    except Exception as e:
        print(f"Warning: Could not save meme: {e}")
        # Last resort - save locally
        save_meme_locally(meme)
        return ""

def save_meme_locally(meme: Dict):
    """
    Fallback function to save meme to local JSON file
    
    Parameters:
        meme: Meme data to save
    """
    try:
        os.makedirs("database", exist_ok=True)
        
        # Load existing memes
        try:
            with open("database/memes.json", "r") as f:
                existing_memes = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_memes = []
        
        # Add new meme
        existing_memes.append(meme)
        
        # Save back
        with open("database/memes.json", "w") as f:
            json.dump(existing_memes, f, indent=2)
        
        print("📁 Saved meme to local JSON fallback")
    except Exception as e:
        print(f"Failed to save locally: {e}")

def get_memes(sort_by: str = 'recent') -> List[Dict]:
    """
    Get memes from database with template information
    
    Parameters:
        sort_by: How to sort ('recent' is the only option for now)
        
    Returns:
        List of meme dictionaries with Cloudinary URLs and template info
    """
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            query = """
                SELECT 
                    m.id,
                    m.cloudinary_url,
                    m.prompt,
                    m.news_url,
                    m.created_at,
                    m.template_id,
                    t.name as template_name,
                    t.description as template_description
                FROM memes m
                LEFT JOIN templates t ON m.template_id = t.id
                ORDER BY m.created_at DESC
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
                    'generated_at': meme['created_at'].isoformat(),
                    'template_id': str(meme['template_id']) if meme['template_id'] else None,
                    'template_name': meme['template_name'],
                    'template_description': meme['template_description']
                })
            
            return formatted_memes
            
    except Exception as e:
        print(f"Error getting memes from database: {e}")
        # Fallback to JSON
        try:
            with open("database/memes.json", "r") as f:
                data = json.loads(f.read())
                if isinstance(data, list):
                    return sorted(data, key=lambda x: x.get('generated_at', ''), reverse=True)[:200]
                else:
                    return []
        except:
            return []

def get_random_templates(count: int = 50) -> List[Dict]:
    """
    Get random meme templates from database
    
    Parameters:
        count: Number of templates to return
        
    Returns:
        List of complete template dictionaries with all fields
    """
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            cur.execute("""
                SELECT 
                    id,
                    name, 
                    description, 
                    usage_context,
                    base_image_url,
                    categories,
                    imgflip_id,
                    popularity_score
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
            
            # Return complete template data
            return [
                {
                    "id": str(template['id']),
                    "name": template['name'],
                    "description": template['description'],
                    "usage_context": template['usage_context'] or "",
                    "base_image_url": template['base_image_url'],
                    "categories": template['categories'] or [],
                    "imgflip_id": template['imgflip_id'],
                    "popularity_score": template['popularity_score']
                }
                for template in templates
            ]
            
    except Exception as e:
        print(f"Error getting templates from database: {e}")
        # Fallback to JSON file
        try:
            with open('database/meme_templates.json', 'r', encoding='utf-8') as f:
                templates = json.load(f)
                # Add mock IDs if not present
                for i, template in enumerate(templates):
                    if 'id' not in template:
                        template['id'] = f"local_{i}"
                return templates[:count]
        except Exception as file_error:
            print(f"Error loading templates from file: {file_error}")
            return []