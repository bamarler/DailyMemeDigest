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
    
    meme_templates = load_meme_templates(len(articles))
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
    if len(prompts) != len(articles):
        raise ValueError(f"Expected {len(articles)} prompts, got {len(prompts)}")
    
    # Combine prompts with original URLs in order
    return [(prompt, article["url"]) for prompt, article in zip(prompts, articles)]


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
    
    # Prepare simplified data for matching
    article_summaries = [
        {
            "index": i,
            "title": art.get("title", ""),
            "description": art.get("description", "")
        }
        for i, art in enumerate(articles)
    ]
    
    meme_list = [
        {"index": i, "description": meme["meme"]}
        for i, meme in enumerate(meme_templates)
    ]
    
    user_prompt = f"""
    Articles to match:
    {json.dumps(article_summaries, indent=2)}
    
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
        enriched_article["meme"] = meme_templates[meme_idx]["meme"]
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
    
    Each article has a "meme" field describing the template to use.
    
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
    
    if content:
        content = content.split("[+")[0].strip()[:500]
    else:
        content = ""
        
    return {
        "title": title,
        "description": description,
        "content": content,
        "source": article.get("source", {}).get("name", "Unknown")
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

# Example usage
if __name__ == "__main__":
    sample_articles = [
        {
            "source": {
            "id": "techcrunch",
            "name": "TechCrunch"
            },
            "author": "Sarah Chen",
            "title": "Apple Finally Admits the iPhone 17 Will Have the Same Features Android Had in 2023",
            "description": "In a surprising press conference, Apple executives proudly announced 'revolutionary' features for the iPhone 17 that Android users have been enjoying for two years.",
            "url": "https://techcrunch.com/2025/06/29/apple-iphone-17-android-features/",
            "urlToImage": "https://techcrunch.com/images/iphone-17-reveal.jpg",
            "publishedAt": "2025-06-29T14:30:00Z",
            "content": "Apple's keynote yesterday revealed the iPhone 17's 'groundbreaking' always-on display, USB-C charging, and 120Hz refresh rate across all models. Android manufacturers responded with a collective eye roll, pointing out these features have been standard since 2023. 'We're thinking different,' said Tim Cook, apparently referring to their timeline rather than their technology. Samsung's social media team simply posted a calendar showing the year 2023 circled in red."
        },
        {
            "source": {
            "id": "wall-street-journal",
            "name": "The Wall Street Journal"
            },
            "author": "Michael Torres",
            "title": "Man Who Sold All His Bitcoin in 2015 for $500 Now Works at the Same McDonald's That Bitcoin Could Have Bought",
            "description": "Local man Jeremy Peterson reflects on his decision to sell 1,000 Bitcoin for $500 to buy a gaming PC, now worth approximately $65 million at current prices.",
            "url": "https://wsj.com/articles/bitcoin-regret-mcdonalds-2025/",
            "urlToImage": "https://wsj.com/images/bitcoin-regret.jpg",
            "publishedAt": "2025-06-29T09:15:00Z",
            "content": "Jeremy Peterson, 34, starts his shift at McDonald's every morning at 6 AM, walking past a 'Now Accepting Bitcoin' sign that serves as a daily reminder of what could have been. In 2015, Peterson sold his entire Bitcoin holdings - 1,000 coins - for $500 to purchase a gaming PC. That PC broke in 2017. The Bitcoin would now be worth $65 million. 'I try not to think about it,' Peterson said while operating the fry station, 'but then customers pay with crypto and I die a little inside.'"
        },
        {
            "source": {
            "id": "cnn",
            "name": "CNN"
            },
            "author": "Rebecca Liu",
            "title": "Zoom Announces Mandatory Return to Office Policy for All Remote Work Software Developers",
            "description": "In an ironic twist, the company that enabled remote work worldwide now requires its employees to commute to offices five days a week.",
            "url": "https://cnn.com/2025/06/29/tech/zoom-return-office-irony/",
            "urlToImage": "https://cnn.com/images/empty-zoom-call.jpg",
            "publishedAt": "2025-06-29T11:45:00Z",
            "content": "Zoom Video Communications announced today that all employees must return to physical offices full-time starting next month, including the team that develops their remote collaboration software. The announcement was made, ironically, via a company-wide Zoom call. 'We believe that in-person collaboration is essential for innovation,' said CEO Eric Yuan from his home office, before realizing his camera was still on. Employee responses ranged from confusion to creating memes about the company becoming its own worst customer."
        },
        {
            "source": {
            "id": "the-verge",
            "name": "The Verge"
            },
            "author": "Daniel Park",
            "title": "Tesla's New 'Unbreakable' Cybertruck Windows Break During Live Demo... Again",
            "description": "History repeats itself as Tesla's 'improved' Cybertruck window demonstration goes exactly as wrong as the 2019 original.",
            "url": "https://theverge.com/2025/06/29/tesla-cybertruck-window-break-again/",
            "urlToImage": "https://theverge.com/images/broken-cybertruck-window.jpg",
            "publishedAt": "2025-06-29T16:20:00Z",
            "content": "Elon Musk stood frozen on stage as the 'completely redesigned, absolutely unbreakable' Cybertruck window shattered into a spider web of cracks, mirroring the infamous 2019 demonstration. 'Well, at least we're consistent,' Musk quipped to nervous laughter. The lead engineer was seen updating his LinkedIn profile from his phone during the remainder of the presentation. Tesla stock dropped 3% within minutes, while meme stocks of glass repair companies surged."
        },
        {
            "source": {
            "id": "bloomberg",
            "name": "Bloomberg"
            },
            "author": "James Mitchell",
            "title": "Netflix Introduces New $25/Month 'Ultra Premium' Tier That Removes Features From Existing Plans",
            "description": "Streaming giant unveils pricing strategy that locks 4K viewing and downloads behind highest tier while removing them from current premium subscribers.",
            "url": "https://bloomberg.com/news/articles/netflix-ultra-premium-features/",
            "urlToImage": "https://bloomberg.com/images/netflix-pricing.jpg",
            "publishedAt": "2025-06-29T08:00:00Z",
            "content": "Netflix announced its new 'Ultra Premium' tier today, priced at $24.99/month, while simultaneously removing 4K streaming and offline downloads from its current $19.99 Premium plan. Current Premium subscribers expressed outrage as they learned they'd need to pay an additional $5 monthly to retain features they already had. 'We're always looking for ways to enhance the customer experience,' said Netflix's pricing director, apparently with a straight face. The announcement led to a 400% increase in Google searches for 'how to cancel Netflix' within hours."
        }
    ]
    
    try:
        prompts = generate_meme_prompts(sample_articles)
        print(f"\nGenerated {len(prompts)} meme prompts:\n")
        for i, (prompt, url) in enumerate(prompts, 1):
            print(f"{i}. URL: {url}")
            print(f"   Prompt: {prompt}")
            print("-" * 80)
    except Exception as e:
        print(f"Error: {e}")