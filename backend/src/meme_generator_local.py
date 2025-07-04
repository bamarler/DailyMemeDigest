"""
Meme generator that creates images with SD and adds text overlay with PIL
Uses Gemini to intelligently extract and format meme text
"""

import torch
from diffusers import AutoPipelineForText2Image
from PIL import Image, ImageDraw, ImageFont
import io
import os
import base64
import json
import re
from typing import List, Tuple, Dict
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from src.database import save_meme
# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Check CUDA availability
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🖥️ Using device: {DEVICE}")

# Global pipeline
PIPELINE = None
MODEL_ID = "stabilityai/sdxl-turbo"  # or any SD model


def initialize_pipeline():
    """Initialize SD pipeline"""
    global PIPELINE
    
    if PIPELINE is not None:
        return
    
    print("🚀 Initializing Stable Diffusion...")
    
    try:
        # Try with fp16 variant first (for models that support it)
        PIPELINE = AutoPipelineForText2Image.from_pretrained(
            MODEL_ID,
            torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
            variant="fp16" if DEVICE == "cuda" else None,
        ).to(DEVICE)
    except ValueError as e:
        if "variant=fp16" in str(e):
            # Fallback for models without fp16 variant (like DreamShaper)
            print("ℹ️ Model doesn't have fp16 variant, using standard precision...")
            PIPELINE = AutoPipelineForText2Image.from_pretrained(
                MODEL_ID,
                torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
            ).to(DEVICE)
        else:
            raise e
    
    print(f"✅ Model loaded: {MODEL_ID}")


def extract_meme_text_with_gemini(prompt: str) -> Dict:
    """
    Use Gemini to intelligently extract text overlays from meme prompt.
    
    Args:
        prompt: Original meme generation prompt
        
    Returns:
        Dict with text positions and content
    """
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    system_prompt = """
    Extract the text that should appear on a meme from the given prompt.
    
    Return a JSON object with the text positions and content. Use these position keys based on meme type:
    - Drake meme: {"top": "rejected text", "bottom": "approved text"}
    - Woman yelling at cat: {"left": "woman's text", "right": "cat's text"}
    - Expanding brain: {"panel1": "text", "panel2": "text", "panel3": "text", etc.}
    - This is fine: {"top": "label for dog", "middle": "label for fire", "bottom": "other labels"}
    - Generic memes: {"top": "top text", "bottom": "bottom text"}
    
    Extract any text that's in quotes or described as labels/text overlays.
    Keep the text short and punchy for meme format.
    
    Return ONLY valid JSON, no other text.
    """
    
    user_prompt = f"Extract meme text from this prompt: {prompt}"
    
    try:
        response = model.generate_content(
            system_prompt + "\n\n" + user_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                response_mime_type="application/json"
            )
        )
        
        text_parts = json.loads(response.text)
        print(f"📝 Gemini extracted text: {text_parts}")
        return text_parts
        
    except Exception as e:
        print(f"⚠️ Gemini extraction failed, using fallback: {e}")
        # Fallback to regex extraction
        return extract_meme_text_fallback(prompt)


def extract_meme_text_fallback(prompt: str) -> Dict:
    """
    Fallback text extraction using regex.
    """
    text_parts = {}
    
    # Find all quoted text
    quotes = re.findall(r"'([^']*)'|\"([^\"]*)\"", prompt)
    texts = [q[0] or q[1] for q in quotes]
    
    # Assign based on meme type
    if "drake" in prompt.lower():
        if len(texts) >= 2:
            text_parts = {"top": texts[0], "bottom": texts[1]}
    elif "woman yelling" in prompt.lower():
        if len(texts) >= 2:
            text_parts = {"left": texts[0], "right": texts[1]}
    else:
        if len(texts) >= 1:
            text_parts["top"] = texts[0]
        if len(texts) >= 2:
            text_parts["bottom"] = texts[1]
    
    return text_parts


def add_text_to_image(image: Image.Image, text_parts: Dict) -> Image.Image:
    """
    Add text overlays to image with proper meme styling.
    Handles various position keys from Gemini extraction.
    
    Args:
        image: PIL Image
        text_parts: Dict with positions and text from Gemini
    
    Returns:
        Image with text overlays
    """
    draw = ImageDraw.Draw(image)
    width, height = image.size
    
    # Try to load Impact font (classic meme font)
    try:
        font_size = int(height * 0.08)  # 8% of image height
        font = ImageFont.truetype("impact.ttf", font_size)
    except:
        try:
            font = ImageFont.load_default()
            font_size = 40
        except:
            font = None
    
    def draw_text_with_outline(text, position, max_width):
        """Draw white text with black outline"""
        # Wrap text if too long
        words = text.upper().split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font:
                bbox = draw.textbbox((0, 0), test_line, font=font)
                text_width = bbox[2] - bbox[0]
            else:
                text_width = len(test_line) * 10
            
            if text_width > max_width and current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                current_line.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Calculate positions
        y_offset = position[1]
        for line in lines:
            if font:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            else:
                text_width = len(line) * 10
                text_height = 20
            
            x = position[0] - text_width // 2
            y = y_offset
            
            # Draw black outline
            outline_width = 3
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), line, font=font, fill="black")
            
            # Draw white text
            draw.text((x, y), line, font=font, fill="white")
            
            y_offset += text_height + 5
    
    # Draw text at different positions
    margin = 20
    max_text_width = width - 2 * margin
    
    # Handle standard positions
    if "top" in text_parts:
        draw_text_with_outline(text_parts["top"], (width // 2, margin), max_text_width)
    
    if "bottom" in text_parts:
        test_text = text_parts["bottom"].upper()
        if font:
            bbox = draw.textbbox((0, 0), test_text, font=font)
            text_height = bbox[3] - bbox[1]
        else:
            text_height = 20
        
        lines = len(text_parts["bottom"].split()) // 5 + 1
        y_pos = height - margin - (text_height * lines)
        draw_text_with_outline(text_parts["bottom"], (width // 2, y_pos), max_text_width)
    
    if "left" in text_parts:
        draw_text_with_outline(text_parts["left"], (width // 4, height // 2), max_text_width // 2)
    
    if "right" in text_parts:
        draw_text_with_outline(text_parts["right"], (3 * width // 4, height // 2), max_text_width // 2)
    
    if "middle" in text_parts:
        draw_text_with_outline(text_parts["middle"], (width // 2, height // 2), max_text_width)
    
    # Handle expanding brain panels
    panel_count = 0
    for key in sorted(text_parts.keys()):
        if key.startswith("panel"):
            panel_count += 1
    
    if panel_count > 0:
        panel_height = height // panel_count
        for i in range(1, panel_count + 1):
            if f"panel{i}" in text_parts:
                y_pos = (i - 0.5) * panel_height
                draw_text_with_outline(text_parts[f"panel{i}"], (width // 2, int(y_pos)), max_text_width)
    
    return image


def generate_meme_image(prompt_url_list: List[Tuple[str, str]], trends: List[str], duration: int) -> str:
    """
    Generate memes with proper text overlays.
    
    Args:
        prompt_url_list: List of (prompt, url) tuples
        
    Returns:
        JSON string with meme results
    """
    initialize_pipeline()
    
    results = []
    
    print(f"🎭 Starting meme generation for {len(prompt_url_list)} prompts...")
    
    for i, (prompt, url) in enumerate(prompt_url_list):
        print(f"\n🎨 Processing {i+1}/{len(prompt_url_list)}: {prompt[:50]}...")
        
        try:
            # Extract text from prompt using Gemini
            text_parts = extract_meme_text_with_gemini(prompt)
            
            # Create simplified prompt for image generation (without text)
            image_prompt = simplify_prompt_for_image(prompt)
            
            # Add explicit no-text instruction
            image_prompt += ", NO TEXT, NO WORDS, NO LETTERS, NO WRITING, NO TYPOGRAPHY, textless, wordless"
            print(f"🖼️ Image prompt: {image_prompt}")
            
            # Generate base image
            with torch.no_grad():
                if "turbo" in MODEL_ID.lower():
                    result = PIPELINE(
                        prompt=image_prompt,
                        num_inference_steps=1,
                        guidance_scale=0.0,
                        width=512,
                        height=512
                    )
                else:
                    result = PIPELINE(
                        prompt=image_prompt,
                        negative_prompt="text, words, letters, numbers, watermark, typography, writing, captions, labels, subtitles, deformed face, ugly face, distorted face, blurry face",
                        num_inference_steps=25,  # More steps for better faces
                        guidance_scale=7.5,      # Slightly higher for quality
                        width=512,
                        height=512
                    )
            
            # Add text overlay
            image = result.images[0]
            if text_parts:
                image = add_text_to_image(image, text_parts)
                print("✅ Added text overlay")
            
            # Convert to base64
            buffered = io.BytesIO()
            image.save(buffered, format="PNG", optimize=True)
            png_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            # Create result
            meme_result = {
                "success": True,
                "prompt": prompt,
                "url": url,
                "png_base64": png_base64,
                "timestamp": datetime.now().isoformat(),
                "trends": trends,
                "duration": duration,
                "text_overlays": text_parts
            }
            save_meme(meme_result)
            results.append(meme_result)
            print(f"✅ Successfully generated meme {i+1}")
            
            # Save for debugging
            if os.getenv("SAVE_MEMES_TO_DISK", "false").lower() == "true":
                os.makedirs("generated_memes", exist_ok=True)
                image.save(f"generated_memes/meme_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            
        except Exception as e:
            print(f"❌ Failed: {e}")
            failed_meme_result = {
                "success": False,
                "prompt": prompt,
                "url": url,
                "png_base64": "",
                "error": str(e),
                "trends": trends,
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            }
            save_meme(failed_meme_result)
            results.append(failed_meme_result)
    successful_count = len([r for r in results if r["success"]])
    # Create response
    response = {
        "success": successful_count > 0,
        "total_count": len(prompt_url_list),
        "successful_count": successful_count,
        "failed_count": len([r for r in results if not r["success"]]),
        "memes": results,
        "generated_at": datetime.now().isoformat()
    }
    
    print(f"\n🎉 Complete! {response['successful_count']}/{response['total_count']} successful")
    
    return json.dumps(response, indent=2)


def simplify_prompt_for_image(prompt: str) -> str:
    """
    Remove text references from prompt for better image generation.
    Emphasizes NO TEXT in the image and better face quality.
    """
    # Remove quoted text
    simplified = re.sub(r"'[^']*'|\"[^\"]*\"", "", prompt)
    
    # Clean up the sentence
    simplified = re.sub(r"\s+", " ", simplified)
    simplified = simplified.replace(" where ", " ")
    simplified = simplified.replace(" with ", " ")
    simplified = simplified.replace(" labeled ", " ")
    simplified = simplified.replace(" says ", " ")
    simplified = simplified.replace(" is ", " ")
    
    # Base quality enhancers for faces
    face_enhancers = ", detailed face, clear facial features, well-defined face"
    
    # Add style hints based on meme type
    if "drake" in prompt.lower():
        return f"Drake meme template blank format, two panels, Drake rejecting gesture top panel, Drake pointing approval bottom panel, Drake's face clearly visible{face_enhancers}, meme style, empty template"
    elif "woman yelling at cat" in prompt.lower():
        return f"Woman yelling at cat meme template blank, split panel, angry woman pointing left side with clear facial expression, confused white cat at dinner table right side{face_enhancers}, meme style, empty template"
    elif "expanding brain" in prompt.lower():
        return f"Expanding brain meme template blank, multiple vertical panels showing brain evolution stages, person's face visible{face_enhancers}, glowing brain progression, meme style, empty template"
    elif "this is fine" in prompt.lower():
        return "This is fine meme template blank, cartoon dog sitting in burning room with coffee cup, flames everywhere, cartoon style dog face, meme style, empty template"
    else:
        return simplified + f", meme template style blank{face_enhancers}, digital art, empty template"


# Download Impact font if needed
def download_impact_font():
    """Download Impact font for meme text"""
    import urllib.request
    
    if not os.path.exists("impact.ttf"):
        print("📥 Downloading Impact font...")
        try:
            # You can also use a direct URL to impact.ttf if you have one
            # This is a placeholder - you'll need to find a proper source
            # urllib.request.urlretrieve("URL_TO_IMPACT_FONT", "impact.ttf")
            print("⚠️ Please manually download impact.ttf font for best results")
        except:
            print("⚠️ Could not download Impact font, using default")


if __name__ == "__main__":
    # Ensure we have Impact font
    download_impact_font()
    
    # Test
    test_prompts = [
        ("Create a Drake meme where Drake rejects 'Using expensive AI APIs' and approves 'Running everything locally'", "https://example.com/1"),
        ("Create a This is Fine meme. The dog is labeled 'Developers'. The fire is labeled 'Production Bugs'. The coffee mug says 'It's Fine'.", "https://example.com/2"),
    ]
    
    result_json = generate_meme_image(test_prompts)
    result = json.loads(result_json)
    
    print(f"\n📊 Results Summary:")
    print(f"   Total: {result['total_count']}")
    print(f"   Successful: {result['successful_count']}")
    
    # Save first result
    for meme in result['memes']:
        if meme['success']:
            img_data = base64.b64decode(meme['png_base64'])
            with open("test_meme_with_text.png", "wb") as f:
                f.write(img_data)
            print(f"\n🖼️ Saved: test_meme_with_text.png")
            print(f"📝 Text overlays: {meme.get('text_overlays', {})}")
            break