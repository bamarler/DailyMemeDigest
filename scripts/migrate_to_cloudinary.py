"""
Migration script to move memes from JSON to Cloudinary + Neon
Run this once to migrate existing data
"""

import json
import os
import base64
from datetime import datetime
import cloudinary
import cloudinary.uploader
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

# Configure Neon
DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    """
    Create database connection
    
    Returns:
        psycopg2.connection: Database connection
    """
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def migrate_templates():
    """
    Migrate templates from JSON to Neon
    
    Returns:
        dict: Mapping of template names to IDs
    """
    print("Migrating templates...")
    
    with open('database/meme_templates.json', 'r', encoding='utf-8') as f:
        templates_array = json.load(f)  # This is an array [{}, {}, ...]
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    template_map = {}
    
    # Iterate through the array of template objects
    for i, template_data in enumerate(templates_array):
        try:
            # Extract template name from the meme field (first few words)
            meme_text = template_data.get('meme', '')
            # Use first 50 chars as a template name or create a generic one
            template_name = f"Template_{i+1}"  # Generic name since no name field exists
            
            cur.execute("""
                INSERT INTO templates (name, description, usage_context)
                VALUES (%s, %s, %s)
                ON CONFLICT (name) DO UPDATE
                SET description = EXCLUDED.description,
                    usage_context = EXCLUDED.usage_context
                RETURNING id, name
            """, (
                template_name,
                meme_text,  # Using 'meme' field as description
                template_data.get('usage_context', '')
            ))
            
            result = cur.fetchone()
            template_map[template_name] = result['id']
            print(f"  ✓ Migrated template: {template_name}")
            
        except Exception as e:
            print(f"  ✗ Error migrating template {i+1}: {e}")
            conn.rollback()
            continue
    
    conn.commit()
    cur.close()
    conn.close()
    
    return template_map

def upload_to_cloudinary(base64_image, meme_data, index):
    """
    Upload base64 image to Cloudinary with metadata
    
    Parameters:
        base64_image: Base64 encoded image string
        meme_data: Dictionary with meme metadata
        index: Index for naming
        
    Returns:
        tuple: (cloudinary_url, public_id) or (None, None) if failed
    """
    try:
        # Remove data:image/png;base64, prefix if present
        if base64_image.startswith('data:'):
            base64_image = base64_image.split(',')[1]
        
        # Convert base64 to bytes
        image_bytes = base64.b64decode(base64_image)
        
        # Generate a unique public_id
        date_str = datetime.now().strftime('%Y/%m')
        public_id = f"memes/{date_str}/meme_{uuid.uuid4().hex[:8]}"
        
        # Upload to Cloudinary with metadata - NOW AS WEBP!
        response = cloudinary.uploader.upload(
            BytesIO(image_bytes),
            public_id=public_id,
            folder="memes",
            resource_type="image",
            format="webp",  # Force WebP format
            quality="auto:good",  # Let Cloudinary optimize quality
            context={
                "prompt": meme_data.get('prompt', ''),
                "news_url": meme_data.get('url', ''),  # Changed from 'news_url' to 'url'
                "created_at": meme_data.get('generated_at', datetime.now().isoformat())
            },
            tags=meme_data.get('trends_used', [])  # Changed from 'trends' to 'trends_used'
        )
        
        print(f"  ✓ Uploaded to Cloudinary as WebP: {public_id}")
        return response['secure_url'], response['public_id']
        
    except Exception as e:
        print(f"  ✗ Error uploading to Cloudinary: {e}")
        return None, None

def migrate_memes(template_map):
    """
    Migrate memes from JSON to Cloudinary + Neon
    
    Parameters:
        template_map: Dictionary mapping template names to IDs
    """
    print("\nMigrating memes...")
    
    with open('database/memes.json', 'r', encoding='utf-8') as f:
        memes_list = json.load(f)  # This is already an array [{}, {}, ...]
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    success_count = 0
    total_count = len(memes_list)
    
    for i, meme in enumerate(memes_list):
        print(f"\nProcessing meme {i+1}/{total_count}...")
        
        # Skip failed memes
        if not meme.get('success', True):
            print(f"  ✗ Skipping meme {i+1} - marked as failed")
            continue
        
        try:
            # Upload image to Cloudinary using png_base64 field
            cloudinary_url, public_id = upload_to_cloudinary(
                meme.get('png_base64', ''),  # Changed from 'image' to 'png_base64'
                meme,
                i
            )
            
            if not cloudinary_url:
                print(f"  ✗ Skipping meme {i+1} - upload failed")
                continue
            
            # Note: template_id will be NULL since memes don't have template info
            # You might need to manually match templates later
            
            # Insert into Neon
            cur.execute("""
                INSERT INTO memes (
                    template_id, 
                    cloudinary_url, 
                    cloudinary_public_id,
                    prompt, 
                    news_url, 
                    created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                None,  # No template info in current meme structure
                cloudinary_url,
                public_id,
                meme.get('prompt', ''),
                meme.get('url', ''),  # Changed from 'news_url' to 'url'
                datetime.fromisoformat(meme.get('generated_at', datetime.now().isoformat()))
            ))
            
            conn.commit()
            success_count += 1
            print(f"  ✓ Migrated meme {i+1} successfully")
            
        except Exception as e:
            print(f"  ✗ Error migrating meme {i+1}: {e}")
            conn.rollback()
            continue
    
    cur.close()
    conn.close()
    
    print(f"\nMigration complete! {success_count}/{total_count} memes migrated successfully")

def main():
    """
    Run the migration
    """
    print("Starting migration process...")
    print("=" * 60)
    
    # Check environment variables
    required_vars = [
        'CLOUDINARY_CLOUD_NAME',
        'CLOUDINARY_API_KEY', 
        'CLOUDINARY_API_SECRET',
        'DATABASE_URL'
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print(f"Error: Missing environment variables: {', '.join(missing)}")
        print("\nPlease set these in your .env file:")
        print("CLOUDINARY_CLOUD_NAME=your-cloud-name")
        print("CLOUDINARY_API_KEY=your-api-key")
        print("CLOUDINARY_API_SECRET=your-api-secret")
        print("DATABASE_URL=your-neon-connection-string")
        return
    
    # Run migrations
    template_map = migrate_templates()
    print(f"\nMigrated {len(template_map)} templates")
    
    migrate_memes(template_map)
    
    print("\n" + "=" * 60)
    print("Migration complete!")

if __name__ == "__main__":
    main()