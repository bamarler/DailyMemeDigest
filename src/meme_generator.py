# ==============================================================================
# FILE: src/meme_generator.py
# AI meme generation logic
# ==============================================================================

from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont
import io
import os
import base64
import json
import random
from typing import Dict, Any, List, Tuple

from datetime import datetime

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


"""Generate memes using OpenAI gpt-image-1 and GPT-3.5"""

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)   
    
    
def generate_meme_image( prompt_url_list: List[Tuple[str, str]]) -> str:
        """
            Generate memes from a list of (prompt, url) tuples
            
            Args:
                prompt_url_list: List of tuples containing (meme_prompt, article_url)
                
            Returns:
                JSON string with meme results
            """
            
        results = []
            
        print(f"🎭 Starting meme generation for {len(prompt_url_list)} prompts...")
            
        for i, (prompt, url) in enumerate(prompt_url_list):
                print(f"\n🎨 Processing {i+1}/{len(prompt_url_list)}: {prompt[:50]}...")
                
                try:
                    # Generate image using OpenAI
                    result = client.images.generate(
                        model="gpt-image-1",
                        prompt=prompt + "RULES: Make text legible so that it shows in the image properly."
                        # size="1024x1024",
                        # response_format="b64_json"
                    )
                    
                    # Get base64 image data
                    png_base64 = result.data[0].b64_json
                    
                    # Create successful result
                    meme_result = {
                        "success": True,
                        "prompt": prompt,
                        "url": url,
                        "png_base64": png_base64,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    results.append(meme_result)
                    print(f"✅ Successfully generated meme for prompt {i+1}")
                    
                except Exception as e:
                    print(f"❌ Failed to generate meme for prompt {i+1}: {e}")
                    
                    # Create failed result
                    meme_result = {
                        "success": False,
                        "prompt": prompt,
                        "url": url,
                        "png_base64": "",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                        
                    }
                    
                    results.append(meme_result)
            
            # Create final JSON response
        response = {
                "success": True,
                "total_count": len(prompt_url_list),
                "successful_count": len([r for r in results if r["success"]]),
                "failed_count": len([r for r in results if not r["success"]]),
                "memes": results,
                "generated_at": datetime.now().isoformat()
            }
            
        print(f"\n🎉 Generation complete! {response['successful_count']}/{response['total_count']} successful")
            
        return json.dumps(response, indent=2)

if __name__ == "__main__":
    # Test with sample prompts
    test_prompts = [
        ("Create a 'Hard to swallow pills' meme. Top panel: hands holding a 'Hard to swallow pills' bottle, label reads '40% of AI Agent Projects Canceled By 2027'. Bottom panel: hand holding two pills labeled 'AI Hype' and 'Reality'", "https://example.com/article1"),
    ]
    
    # Generate and print results
    result_json = generate_meme_image(test_prompts)
    result = json.loads(result_json)
    
    print(f"\n:bar_chart: Results Summary:")
    print(f"   Total: {result['total_count']}")
    print(f"   Successful: {result['successful_count']}")
    print(f"   Failed: {result['failed_count']}")
    
    # Optionally save first successful image for viewing
    for meme in result['memes']:
        if meme['success']:
            img_data = base64.b64decode(meme['png_base64'])
            with open("test_meme.png", "wb") as f:
                f.write(img_data)
            print(f"\n:frame_photo: Test image saved as test_meme.png")
            break

