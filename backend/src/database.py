import os
import json
from typing import Dict

def save_meme(meme: Dict):
    """
    Save a single meme to database
    
    Parameters:
    - meme: Single meme generation result
    """
    try:
        os.makedirs("database", exist_ok=True)
        
        try:
            with open("database/memes.json", "r") as f:
                existing_memes = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_memes = []
        
        existing_memes.append(meme)
        
        with open("database/memes.json", "w") as f:
            json.dump(existing_memes, f, indent=2)
        
    except Exception as e:
        print(f"Warning: Could not save meme: {e}")