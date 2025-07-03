"""
Scraper to fetch popular meme templates from Imgflip API
and enrich them with descriptions using Gemini
"""

import json
import os
import time
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
import google.generativeai as genai
import cloudinary
import cloudinary.uploader
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

# Configure APIs
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

DATABASE_URL = os.getenv('DATABASE_URL')
IMGFLIP_API_URL = "https://api.imgflip.com/get_memes"

def get_db_connection():
    """
    Create database connection
    
    Returns:
        psycopg2.connection: Database connection
    """
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def fetch_imgflip_memes() -> List[Dict]:
    """
    Fetch meme templates from Imgflip API
    
    Returns:
        List of meme dictionaries
    """
    print("Fetching memes from Imgflip API...")
    response = requests.get(IMGFLIP_API_URL)
    data = response.json()
    
    if not data.get('success'):
        raise Exception("Failed to fetch memes from Imgflip")
    
    memes = data['data']['memes']
    print(f"Fetched {len(memes)} meme templates")
    return memes

def upload_template_to_cloudinary(meme_url: str, meme_name: str, imgflip_id: str) -> Optional[str]:
    """
    Upload meme template image to Cloudinary
    
    Parameters:
        meme_url: URL of the meme image
        meme_name: Name of the meme
        imgflip_id: Imgflip ID
        
    Returns:
        Cloudinary URL or None if failed
    """
    try:
        public_id = f"meme_templates/{imgflip_id}"
        
        response = cloudinary.uploader.upload(
            meme_url,
            public_id=public_id,
            folder="meme_templates",
            format="webp",  # Convert to WebP
            quality="auto:good",  # Optimize quality
            tags=["template", "imgflip"],
            context={
                "meme_name": meme_name,
                "source": "imgflip"
            }
        )
        
        return response['secure_url']
        
    except Exception as e:
        print(f"Error uploading {meme_name} to Cloudinary: {e}")
        return None

def enrich_memes_with_gemini(memes: List[Dict], batch_size: int = 50) -> List[Dict]:
    """
    Use Gemini to generate descriptions, categories, and usage context
    
    Parameters:
        memes: List of meme dictionaries
        batch_size: Number of memes to process at once
        
    Returns:
        Enriched meme list
    """
    model = genai.GenerativeModel('gemini-2.0-flash')
    enriched_memes = []
    
    # Process in batches
    for i in range(0, len(memes), batch_size):
        batch = memes[i:i + batch_size]
        print(f"\nProcessing batch {i//batch_size + 1} ({len(batch)} memes)...")
        
        # Prepare batch for Gemini
        meme_names = [{"id": m["id"], "name": m["name"]} for m in batch]
        
        prompt = f"""
        You are a meme culture expert. For each meme template below, provide:
        1. A description of what the meme looks like and depicts
        2. Usage context (when/how it's typically used)
        3. Categories (relevant tags like "reaction", "comparison", "pop culture", etc.)
        
        Output format: JSON array with objects containing:
        - id: the imgflip id
        - description: detailed description of the meme including visually what is depicted (assume the reader has no prior visual or literary context of the meme)
        - usage_context: when and how to use this meme
        - categories: array of category strings
        
        Memes to analyze:
        {json.dumps(meme_names, indent=2)}
        """
        
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.7,
                    response_mime_type="application/json"
                )
            )
            
            enriched_batch = json.loads(response.text)
            
            # Merge enrichment with original data
            enrichment_map = {e["id"]: e for e in enriched_batch}
            
            for meme in batch:
                if meme["id"] in enrichment_map:
                    meme.update(enrichment_map[meme["id"]])
                enriched_memes.append(meme)
            
            # Rate limit protection
            time.sleep(2)
            
        except Exception as e:
            print(f"Error enriching batch: {e}")
            # Add unenriched memes if Gemini fails
            enriched_memes.extend(batch)
    
    return enriched_memes

def update_database(memes: List[Dict]):
    """
    Update database with meme templates
    
    Parameters:
        memes: List of enriched meme dictionaries
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    success_count = 0
    
    for rank, meme in enumerate(memes, 1):
        try:
            # Check if template exists
            cur.execute("""
                SELECT id, times_seen FROM templates WHERE imgflip_id = %s
            """, (meme["id"],))
            
            existing = cur.fetchone()
            
            # Upload to Cloudinary
            cloudinary_url = upload_template_to_cloudinary(
                meme["url"], 
                meme["name"], 
                meme["id"]
            )
            
            if existing:
                # Update existing template
                cur.execute("""
                    UPDATE templates SET
                        imgflip_rank = %s,
                        times_seen = times_seen + 1,
                        last_seen = CURRENT_TIMESTAMP,
                        base_image_url = COALESCE(%s, base_image_url)
                    WHERE imgflip_id = %s
                """, (rank, cloudinary_url, meme["id"]))
                
                print(f"  ✓ Updated: {meme['name']} (seen {existing['times_seen'] + 1} times)")
                
            else:
                # Insert new template
                cur.execute("""
                    INSERT INTO templates (
                        name, description, categories, usage_context,
                        base_image_url, imgflip_id, imgflip_rank,
                        popularity_score, times_seen
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    meme["name"],
                    meme.get("description", f"The {meme['name']} meme template"),
                    meme.get("categories", ["general"]),
                    meme.get("usage_context", ""),
                    cloudinary_url or meme["url"],  # Fallback to imgflip URL
                    meme["id"],
                    rank,
                    1000 - rank,  # Higher rank = higher score
                    1
                ))
                
                print(f"  ✓ Added: {meme['name']} (rank #{rank})")
            
            conn.commit()
            success_count += 1
            
        except Exception as e:
            print(f"  ✗ Error with {meme['name']}: {e}")
            conn.rollback()
    
    cur.close()
    conn.close()
    
    print(f"\nDatabase update complete! {success_count}/{len(memes)} templates processed")

def main(batch_size: int = 50):
    """
    Main scraper function
    
    Parameters:
        batch_size: Batch size for Gemini processing
    """
    print("Starting Imgflip meme template scraper...")
    print("=" * 60)
    
    # Fetch memes
    memes = fetch_imgflip_memes()
    
    # Enrich with descriptions
    print("\nEnriching memes with descriptions...")
    enriched_memes = enrich_memes_with_gemini(memes, batch_size)
    
    # Update database
    print("\nUpdating database...")
    update_database(enriched_memes)
    
    print("\n" + "=" * 60)
    print("Scraping complete!")

if __name__ == "__main__":
    main(batch_size=50)