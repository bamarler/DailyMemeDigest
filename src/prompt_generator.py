"""
Pre-meme prompter that converts news articles into meme generation prompts.
Takes articles from NewsAPI and pairs them with meme templates to create prompts.

Setup:
    pip install google-generativeai python-dotenv
    
    Create .env file with:
    GEMINI_API_KEY=your-api-key-here
"""

import json
import os
from typing import List, Dict, Tuple
import google.generativeai as genai
from dotenv import load_dotenv
import random
from src.database import get_random_templates

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")
    
genai.configure(api_key=api_key)


def generate_meme_prompts(articles: List[Dict]) -> List[Tuple[str, str]]:
    """
    Main entry point that converts articles into meme prompts.
    Uses two LLM calls: first to match, then to generate prompts.
    
    Args:
        articles: List of article dictionaries from NewsAPI
        
    Returns:
        List of tuples containing (meme_prompt, article_url)
    """
    if not articles:
        return []
    
    meme_templates = get_random_templates(len(articles) * 3)
    print(f"found {len(meme_templates)} meme templates.")
    
    # Step 1: Get semantic matches between articles and memes
    matches = get_article_meme_matches(articles, meme_templates)
    print(f"{len(matches)} matches")
    
    # Step 2: Enrich articles with matched memes
    enriched_articles = enrich_articles_with_memes(articles, meme_templates, matches)
    print(f"{len(enriched_articles)} enriched_articles")
    # Step 3: Generate prompts for the matched pairs
    prompts = generate_prompts_from_matches(enriched_articles)
    print(f"generated {len(prompts)}")
    
    # Validate output length
    if len(prompts) != len(enriched_articles):
        raise ValueError(f"Expected {len(enriched_articles)} prompts, got {len(prompts)}")
    
    # Combine prompts with original URLs in order
    return [(prompt, article["url"], article["meme_template"]["id"]) for prompt, article in zip(prompts, enriched_articles)]


def get_article_meme_matches(articles: List[Dict], meme_templates: List[Dict]) -> List[int]:
    """
    Use Gemini to semantically match articles with memes.
    
    Args:
        articles: List of article dictionaries
        meme_templates: List of meme templates
        
    Returns:
        List of meme indices corresponding to each article
    """
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    system_prompt = """
    You are an expert at matching news articles with meme templates based on semantic relevance.
    
    Your task is to match each article with the MOST APPROPRIATE meme template based on:
    1. Thematic relevance (e.g., comparison memes for articles about competition)
    2. Emotional tone (e.g., disaster memes for bad news)
    3. Structural fit (e.g., "two options" memes for dilemma articles)
    4. Humor potential
    
    Rules:
    - Each meme can only be used ONCE
    - Think carefully about which meme best captures each article's essence
    - Don't just match in order - find the BEST semantic matches
    
    Output format: A JSON array of meme indices (0-based) in article order.
    For example: [7, 2, 9, 0, 5] means:
    - Article 0 matches with meme 7
    - Article 1 matches with meme 2
    - etc.
    """
    
    meme_list = [
        {"index": i, "name": meme["name"], "description": meme["description"], "usage_context": meme["usage_context"]}
        for i, meme in enumerate(meme_templates)
    ]
    
    user_prompt = f"""
    Articles to match:
    {json.dumps(articles, indent=2)}
    
    Available meme templates:
    {json.dumps(meme_list, indent=2)}
    
    Match each article with the most semantically appropriate meme.
    Return ONLY a JSON array of meme indices. The array must have {len(articles)} elements.
    Each meme index can only appear once.
    """
    
    try:
        response = model.generate_content(
            system_prompt + "\n\n" + user_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.7,
                response_mime_type="application/json"
            )
        )
        
        matches = json.loads(response.text)
        
        # Validate
        if not isinstance(matches, list) or len(matches) != len(articles):
            raise ValueError(f"Expected list of {len(articles)} indices")
            
        # Check for duplicates
        # if len(set(matches)) != len(matches):
        #     raise ValueError("Duplicate meme assignments detected")
            
        # Check indices are valid
        for idx in matches:
            if not isinstance(idx, int) or idx < 0 or idx >= len(meme_templates):
                raise ValueError(f"Invalid meme index: {idx}")
                
        return matches
        
    except Exception as e:
        raise Exception(f"Error in matching phase: {e}")


def enrich_articles_with_memes(articles: List[Dict], meme_templates: List[Dict], matches: List[int]) -> List[Dict]:
    """
    Add matched meme descriptions to articles.
    
    Args:
        articles: Original articles
        meme_templates: Meme template list
        matches: List of meme indices for each article
        
    Returns:
        Articles with 'meme' field added
    """
    enriched = []
    for article, meme_idx in zip(articles, matches):
        enriched_article = prepare_article(article)
        enriched_article["meme_template"] = meme_templates[meme_idx]
        enriched.append(enriched_article)
    return enriched


def generate_prompts_from_matches(enriched_articles: List[Dict]) -> List[str]:
    """
    Generate meme prompts from pre-matched article-meme pairs.
    
    Args:
        enriched_articles: Articles with 'meme' field included
        
    Returns:
        List of prompt strings
    """
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    system_prompt = """
    You are a meme generation expert. Given articles that have already been matched with meme templates,
    create specific, funny meme prompts.
    
    Each article has a "meme_template" field containing the template to use.
    
    For each article:
    1. Create a prompt that specifically uses that meme format
    2. Include specific text overlays that reference the article content
    3. Make it topical, clever, and funny
    4. Include a description of precisely what the meme looks like assuming that whoever reads it has NEVER seen the meme before.
    
    Output format: JSON array of prompt strings in the same order as input.
    Example: [
        "Create a Drake meme where Drake rejects 'Old Bitcoin mining' and approves 'American Bitcoin with tariffs'",
        "Create a Woman yelling at cat meme where the woman represents 'Wall Street' yelling 'We need stablecoins!' and the cat is 'Bitcoin' looking confused"
    ]
    """
    
    user_prompt = f"""
    Articles with pre-matched memes:
    {json.dumps(enriched_articles, indent=2)}
    
    Generate a meme prompt for each article using its assigned meme template.
    Return ONLY a JSON array of {len(enriched_articles)} prompt strings.
    """
    
    try:
        response = model.generate_content(
            system_prompt + "\n\n" + user_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.8,
                response_mime_type="application/json"
            )
        )
        
        prompts = json.loads(response.text)
        
        if not isinstance(prompts, list) or len(prompts) != len(enriched_articles):
            raise ValueError(f"Expected {len(enriched_articles)} prompts")
            
        return prompts
        
    except Exception as e:
        raise Exception(f"Error in prompt generation phase: {e}")


def prepare_article(article: Dict) -> Dict:
    """
    Prepare a single article for processing.
    
    Args:
        article: Raw article dictionary
        
    Returns:
        Cleaned article dictionary
    """
    title = article.get("title", "").strip()
    description = article.get("description", "").strip()
    content = article.get("content", "")
    url = article.get("url", "")
    
    if content:
        content = content.split("[+")[0].strip()[:500]
    else:
        content = ""
        
    return {
        "title": title,
        "description": description,
        "content": content,
        "url": url,
    }


def load_meme_templates(num_articles: int) -> List[Dict[str, str]]:
    """
    Load meme templates from JSON file.
    
    Returns:
        List of meme dictionaries with 'meme' field containing description
    """
    with open('database/meme_templates.json', 'r', encoding='utf-8') as f:
        templates = json.load(f)
        
    if not isinstance(templates, list):
        raise ValueError("meme_templates.json must contain a JSON array")
        
    for template in templates:
        if not isinstance(template, dict) or 'meme' not in template:
            raise ValueError("Each meme template must have a 'meme' field")
            
    return random.sample(templates, num_articles * 3)