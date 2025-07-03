# ==============================================================================
# FILE: src/meme_generator.py
# AI meme generation logic - Updated to save directly to Cloudinary
# ==============================================================================

from openai import OpenAI
import os
import json
from typing import List, Tuple
from datetime import datetime
from dotenv import load_dotenv
from src.database import save_meme

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))   
    
    
def generate_meme_image(prompt_url_template_list: List[Tuple[str, str, str]], trends: List[str], duration: int, quality: str = "medium") -> str:
    """
    Generate memes from a list of (prompt, url, template_id) tuples
    
    Parameters:
        prompt_url_template_list: List of tuples containing (meme_prompt, article_url, template_id)
        trends: List of trends used for meme generation
        duration: Duration in days for meme generation
        quality: Image quality setting for OpenAI
        
    Returns:
        JSON string with meme results containing Cloudinary URLs
    """
    results = []
    
    print(f"🎭 Starting meme generation for {len(prompt_url_template_list)} prompts...")
    
    for i, (prompt, url, template_id) in enumerate(prompt_url_template_list):
        print(f"\n🎨 Processing {i+1}/{len(prompt_url_template_list)}: {prompt[:50]}...")
        
        try:
            result = client.images.generate(
                model="gpt-image-1",
                prompt=prompt + "RULES: Make text legible so that it shows in the image properly; ensure that all important text is within the image frame.",
                size="1024x1024",
                quality=quality,
                response_format="b64_json"
            )
            
            b64_json = result.data[0].b64_json
            
            meme_data = {
                "success": True,
                "prompt": prompt,
                "url": url,
                "png_base64": b64_json,
                "trends_used": trends,
                "duration_days": duration,
                "timestamp": datetime.now().isoformat(),
                "template_id": template_id
            }
            
            cloudinary_url = save_meme(meme_data)
            
            meme_result = {
                "success": True,
                "prompt": prompt,
                "url": url,
                "image": cloudinary_url,
                "trends_used": trends,
                "duration_days": duration,
                "generated_at": datetime.now().isoformat(),
                "template_id": template_id
            }
            
            results.append(meme_result)
            print(f"✅ Successfully generated meme for prompt {i+1}")
            
        except Exception as e:
            print(f"❌ Failed to generate meme for prompt {i+1}: {e}")
            
            meme_result = {
                "success": False,
                "prompt": prompt,
                "url": url,
                "error": str(e),
                "trends_used": trends,
                "duration_days": duration,
                "generated_at": datetime.now().isoformat(),
                "template_id": template_id
            }
            results.append(meme_result)
    
    successful_count = len([r for r in results if r["success"]])
    response = {
        "success": successful_count > 0,
        "total_count": len(prompt_url_template_list),
        "successful_count": successful_count,
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
    result_json = generate_meme_image(test_prompts, trends=["AI", "artificial intelligence", "machine learning"], duration=1)
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

