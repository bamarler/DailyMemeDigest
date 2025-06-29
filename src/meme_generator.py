# ==============================================================================
# FILE: src/meme_generator.py
# AI meme generation logic
# ==============================================================================

from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import json
import random
from typing import Dict, Any
from .models import NewsItem
from .config import Config

class AIMemeGenerator:
    """Generate memes using OpenAI gpt-image-1 and GPT-3.5"""
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.templates = [
            "drake_pointing", "expanding_brain", "distracted_boyfriend", 
            "this_is_fine", "two_buttons", "woman_yelling_at_cat"
        ]
        
        # Template configurations
        self.template_configs = {
            "drake_pointing": {
                "description": "Two-panel meme with rejection (top) and approval (bottom)",
                "text_positions": [
                    {"x": 520, "y": 200, "width": 400, "type": "top_text"},
                    {"x": 520, "y": 600, "width": 400, "type": "bottom_text"}
                ]
            },
            "expanding_brain": {
                "description": "Four-level brain evolution from basic to galaxy brain",
                "text_positions": [
                    {"x": 580, "y": 120, "width": 350, "type": "level1"},
                    {"x": 580, "y": 260, "width": 350, "type": "level2"},
                    {"x": 580, "y": 440, "width": 350, "type": "level3"},
                    {"x": 580, "y": 620, "width": 350, "type": "level4"}
                ]
            },
            "distracted_boyfriend": {
                "description": "Three-person scene with distraction dynamic",
                "text_positions": [
                    {"x": 150, "y": 100, "width": 200, "type": "girlfriend"},
                    {"x": 400, "y": 400, "width": 200, "type": "boyfriend"},
                    {"x": 700, "y": 150, "width": 200, "type": "distraction"}
                ]
            },
            "this_is_fine": {
                "description": "Calm character in chaotic situation",
                "text_positions": [
                    {"x": 512, "y": 850, "width": 600, "type": "caption", "center": True}
                ]
            },
            "two_buttons": {
                "description": "Person choosing between two difficult options",
                "text_positions": [
                    {"x": 200, "y": 300, "width": 250, "type": "button1"},
                    {"x": 600, "y": 300, "width": 250, "type": "button2"},
                    {"x": 512, "y": 700, "width": 400, "type": "caption", "center": True}
                ]
            },
            "woman_yelling_at_cat": {
                "description": "Split scene with emotional contrast",
                "text_positions": [
                    {"x": 200, "y": 400, "width": 300, "type": "woman"},
                    {"x": 650, "y": 400, "width": 300, "type": "cat"}
                ]
            }
        }
    
    def generate_meme_text(self, news_item: NewsItem, template_name: str) -> Dict[str, Any]:
        """Generate meme text using GPT-3.5"""
        
        prompts = {
            "drake_pointing": f"""Create a Drake pointing meme about this AI news: "{news_item.title}"

Make it funny and relatable to AI developers/enthusiasts.
Return only valid JSON in this exact format:
{{"top_text": "thing Drake rejects (max 40 chars)", "bottom_text": "thing Drake wants (max 40 chars)"}}""",
            
            "expanding_brain": f"""Create an expanding brain meme about AI evolution based on: "{news_item.title}"

Return only valid JSON in this exact format:
{{"level1": "basic concept (max 30 chars)", "level2": "better concept (max 30 chars)", "level3": "advanced concept (max 30 chars)", "level4": "galaxy brain concept (max 30 chars)"}}""",
            
            "distracted_boyfriend": f"""Create a distracted boyfriend meme about: "{news_item.title}"

Return only valid JSON in this exact format:
{{"girlfriend": "current technology (max 25 chars)", "boyfriend": "developers/users (max 20 chars)", "distraction": "new AI technology (max 25 chars)"}}""",
            
            "this_is_fine": f"""Create a "This is Fine" meme about: "{news_item.title}"

Return only valid JSON in this exact format:
{{"caption": "ironic statement about AI situation being 'fine' (max 50 chars)"}}""",
            
            "two_buttons": f"""Create a two buttons meme about a dilemma from: "{news_item.title}"

Return only valid JSON in this exact format:
{{"button1": "first difficult choice (max 30 chars)", "button2": "second difficult choice (max 30 chars)", "caption": "person's struggle/dilemma (max 35 chars)"}}""",
            
            "woman_yelling_at_cat": f"""Create a woman yelling at cat meme about: "{news_item.title}"

Return only valid JSON in this exact format:
{{"woman": "angry/frustrated statement (max 40 chars)", "cat": "confused/innocent response (max 40 chars)"}}"""
        }
        
        prompt = prompts.get(template_name, prompts["drake_pointing"])
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a hilarious meme generator. Always respond with valid JSON only, no additional text."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.8
            )
            
            content = response.choices[0].message.content.strip()
            
            # Clean response (remove markdown formatting if present)
            if content.startswith('```'):
                content = '\n'.join(content.split('\n')[1:-1])
            
            return json.loads(content)
            
        except Exception as e:
            print(f"⚠️ Text generation error: {e}")
            # Fallback responses
            fallbacks = {
                "drake_pointing": {"top_text": "Old AI", "bottom_text": "New AI"},
                "expanding_brain": {"level1": "Basic AI", "level2": "Smart AI", "level3": "Super AI", "level4": "AI overlords"},
                "distracted_boyfriend": {"girlfriend": "Old tech", "boyfriend": "Developers", "distraction": "New AI"},
                "this_is_fine": {"caption": "AI is evolving rapidly. This is fine."},
                "two_buttons": {"button1": "Embrace AI", "button2": "Resist change", "caption": "Developers everywhere"},
                "woman_yelling_at_cat": {"woman": "AI will replace us all!", "cat": "I just want to help"}
            }
            return fallbacks.get(template_name, {"text": "Meme generation failed"})
    
    def generate_meme_image(self, template_name: str, news_title: str) -> str:
        """Generate meme image using gpt-image-1"""
        
        image_prompts = {
            "drake_pointing": "Drake pointing meme template: Two panels vertically stacked. Top panel shows Drake making a dismissive hand gesture and turning away with disapproving expression. Bottom panel shows the same Drake character pointing enthusiastically with approval and a smile.",
            "expanding_brain": "Four-level expanding brain meme template showing brain evolution. Vertical layout with 4 distinct sections: 1) Normal human brain, 2) Slightly glowing brain, 3) Bright cosmic brain with energy, 4) Transcendent galaxy brain with stars.",
            "distracted_boyfriend": "Distracted boyfriend meme scene: A couple walking together with a man turning his head to look at another attractive person passing by. The girlfriend looks annoyed and disapproving.",
            "this_is_fine": "This is fine meme: A calm anthropomorphic dog character sitting peacefully at a table with a coffee cup while orange flames and chaos surround the room.",
            "two_buttons": "Two buttons meme: A nervous, sweating person in business attire standing in front of two large, prominent buttons or choices. The person appears anxious and conflicted.",
            "woman_yelling_at_cat": "Woman yelling at cat meme: Split scene with two panels. Left panel shows an upset woman pointing and yelling emotionally. Right panel shows a confused white cat at a dinner table."
        }
        
        prompt = image_prompts.get(template_name, image_prompts["drake_pointing"])
        
        full_prompt = f"""{prompt}

Context: Related to AI/technology news about "{news_title[:60]}..."

Style requirements:
- Professional meme format suitable for social media
- High contrast colors for text readability
- Clean, modern illustration style
- Clear designated areas for text placement
- 1024x1024 square format"""
        
        try:
            print(f"🎨 Generating {template_name} image...")
            
            result = self.client.images.generate(
                model="gpt-image-1",
                prompt=full_prompt,
                size="1024x1024",
                response_format="b64_json"
            )
            
            print("✅ Image generated successfully")
            return result.data[0].b64_json
            
        except Exception as e:
            print(f"❌ Image generation failed: {e}")
            return self._create_fallback_image(template_name)
    
    def _create_fallback_image(self, template_name: str) -> str:
        """Create simple fallback image if AI generation fails"""
        try:
            img = Image.new('RGB', (1024, 1024), color='#f8f9fa')
            draw = ImageDraw.Draw(img)
            
            try:
                font_large = ImageFont.truetype("arial.ttf", 64)
                font_small = ImageFont.truetype("arial.ttf", 32)
            except:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            template_title = template_name.replace('_', ' ').title()
            
            # Center the text
            draw.text((512, 400), "🎭", fill='#667eea', font=font_large, anchor="mm")
            draw.text((512, 500), f"{template_title}", fill='#333', font=font_large, anchor="mm")
            draw.text((512, 580), "Meme Template", fill='#666', font=font_small, anchor="mm")
            
            # Convert to base64
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            return base64.b64encode(img_buffer.getvalue()).decode()
            
        except Exception as e:
            print(f"❌ Fallback image creation failed: {e}")
            return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    def add_text_to_image(self, image_base64: str, meme_text: Dict[str, Any], template_name: str) -> str:
        """Add text overlay to image"""
        try:
            # Decode image
            image_bytes = base64.b64decode(image_base64)
            img = Image.open(io.BytesIO(image_bytes))
            draw = ImageDraw.Draw(img)
            
            # Get template configuration
            config = self.template_configs.get(template_name, {})
            positions = config.get("text_positions", [])
            
            # Load fonts
            try:
                font_large = ImageFont.truetype("arial.ttf", 48)
                font_medium = ImageFont.truetype("arial.ttf", 36)
                font_small = ImageFont.truetype("arial.ttf", 28)
            except:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Add text for each position
            for pos in positions:
                text_type = pos.get("type", "")
                text_content = meme_text.get(text_type, "")
                
                if text_content:
                    self._add_outlined_text(
                        draw=draw,
                        text=text_content,
                        x=pos["x"],
                        y=pos["y"],
                        max_width=pos["width"],
                        font=font_medium,
                        center=pos.get("center", False)
                    )
            
            # Convert back to base64
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG', quality=90)
            img_buffer.seek(0)
            return base64.b64encode(img_buffer.getvalue()).decode()
            
        except Exception as e:
            print(f"❌ Text overlay failed: {e}")
            return image_base64
    
    def _add_outlined_text(self, draw, text: str, x: int, y: int, max_width: int, font, center: bool = False):
        """Add text with black outline for better readability"""
        if not text:
            return
        
        # Word wrap
        words = str(text).split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = current_line + [word]
            test_text = " ".join(test_line)
            bbox = draw.textbbox((0, 0), test_text, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(" ".join(current_line))
        
        # Draw text with outline
        line_height = 55
        for i, line in enumerate(lines[:3]):  # Max 3 lines
            line_y = y + i * line_height
            
            # Center alignment if requested
            if center:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                line_x = x - text_width // 2
            else:
                line_x = x
            
            # Black outline
            outline_width = 3
            for adj_x in range(-outline_width, outline_width + 1):
                for adj_y in range(-outline_width, outline_width + 1):
                    if adj_x != 0 or adj_y != 0:
                        draw.text((line_x + adj_x, line_y + adj_y), line, font=font, fill='black')
            
            # White text
            draw.text((line_x, line_y), line, font=font, fill='white')
    
    def create_complete_meme(self, news_item: NewsItem, template_name: str = None) -> Dict[str, Any]:
        """Generate complete meme with AI image and text"""
        if not template_name:
            template_name = random.choice(self.templates)
        
        print(f"🎭 Creating {template_name} meme for: {news_item.title[:50]}...")
        
        try:
            # Step 1: Generate meme text
            meme_text = self.generate_meme_text(news_item, template_name)
            print(f"✍️ Text generated: {meme_text}")
            
            # Step 2: Generate AI image
            image_base64 = self.generate_meme_image(template_name, news_item.title)
            
            # Step 3: Add text overlay
            final_image = self.add_text_to_image(image_base64, meme_text, template_name)
            
            return {
                'success': True,
                'template_name': template_name,
                'meme_text': meme_text,
                'image_data': final_image,
                'news_source': news_item.source,
                'news_title': news_item.title
            }
            
        except Exception as e:
            print(f"❌ Meme generation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
