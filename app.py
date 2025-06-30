# ==============================================================================
# FILE: app.py
# Main Flask application - entry point
# ==============================================================================

from flask import Flask, render_template, request, jsonify
import os
import json
import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv
import click

# Load environment variables
load_dotenv()

from src.news_aggregator import get_news_articles
from src.filter_top_k import get_top_articles
from src.prompt_generator import generate_meme_prompts

# Parse command line arguments
parser = argparse.ArgumentParser(description='AI Meme Factory')
parser.add_argument('--local', action='store_true', help='Use local Stable Diffusion instead of OpenAI')
parser.add_argument('--port', type=int, default=5001, help='Port to run the server on')
args = parser.parse_args()

# Check environment variable as fallback
if not args.local and os.getenv('MEME_MODE', '').lower() == 'local':
    args.local = True

# Dynamic import based on mode
if args.local:
    print("Running in LOCAL mode - using Stable Diffusion")
    try:
        from src.meme_generator_local import generate_meme_image
        print("Successfully imported local meme generator")
    except ImportError as e:
        print("\nError: Missing dependencies for local mode!")
        print("Please install the required packages:")
        print("\n  pip install torch torchvision diffusers transformers accelerate pillow google-generativeai")
        print("\nFor GPU support (recommended):")
        print("  pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118")
        print("\nThen try again with: python app.py --local")
        sys.exit(1)
else:
    print("Running in CLOUD mode - using OpenAI API")
    from src.meme_generator import generate_meme_image

def create_app():
    app = Flask(__name__)
    
    # Configure static files for the separated frontend
    app.static_folder = 'static'
    app.static_url_path = '/static'
    
    # Add custom CLI commands
    @app.cli.command()
    @click.option('--port', default=5001, help='Port to run on')
    def cloud(port):
        """Run in cloud mode (OpenAI)"""
        os.environ['FLASK_RUN_MODE'] = 'cloud'
        app.run(debug=True, host='0.0.0.0', port=port)
    
    @app.cli.command()
    @click.option('--port', default=5001, help='Port to run on')
    def local(port):
        """Run in local mode (Stable Diffusion)"""
        os.environ['FLASK_RUN_MODE'] = 'local'
        app.run(debug=True, host='0.0.0.0', port=port)
    
    @app.route('/')
    def index():
        """Serve the main HTML page"""
        return render_template('index.html')
    
    @app.route('/history')
    def history():
        """Serve the history/previous generations page"""
        return render_template('history.html')
    
    @app.route('/api/generate', methods=['POST'])
    def generate_meme():
        """
        Generate memes based on user preferences
        
        Parameters:
        - JSON body with 'trends' (list) and 'duration' (int)
        
        Returns:
        - JSON response with generated memes (only successful ones)
        """
        try:
            print("Starting meme generation...")
            print(f"Mode: {'LOCAL' if args.local else 'CLOUD'}")
            
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
            
            trends = data.get('trends', [])
            duration = data.get('duration', 1)
            memes = data.get('memes', 10)
            
            print(f"Request: Trends={trends}, Duration={duration} days, Memes={memes}")
            
            if not trends:
                return jsonify({
                    'success': False,
                    'error': 'Please select at least one AI trend'
                }), 400
            
            print("Fetching articles...")
            articles = get_news_articles(trends, days_back=duration)
            
            if not articles:
                return jsonify({
                    'success': False,
                    'error': 'No articles found for selected trends'
                })
            
            print(f"Filtering top articles from {len(articles)} total...")
            top_articles = get_top_articles(articles, memes, trends)
            
            print("Generating prompts...")
            prompts = generate_meme_prompts(top_articles)
            print(f"Generated prompts: {prompts}")
            
            if not prompts:
                return jsonify({
                    'success': False,
                    'error': 'Failed to generate meme prompts'
                })
            
            print("Generating memes...")
            memes = generate_meme_image(prompts, trends, duration)
            
            if isinstance(memes, str):
                try:
                    parsed_memes = json.loads(memes)
                except json.JSONDecodeError:
                    return jsonify({
                        'success': False,
                        'error': 'Invalid response from meme generator'
                    }), 500
            else:
                parsed_memes = memes

            successful_memes = [meme for meme in parsed_memes["memes"] if meme.get("success", False)]
            
            # Create filtered response with only successful memes
            filtered_response = {
                "success": True,
                "memes": successful_memes,
                "total_generated": len(parsed_memes.get("memes", [])),
                "successful_count": len(successful_memes)
            }
            
            return jsonify(filtered_response)
                
        except Exception as e:
            print(f"Error in meme generation: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Meme generation failed: {str(e)}'
            }), 500
    
    @app.route('/api/memes')
    def get_memes():
        """Get existing memes from database"""
        try:
            sort_by = request.args.get('sort', 'recent')
            
            try:
                with open("database/memes.json", "r") as f:
                    data = json.loads(f.read())
                    # Handle both list and dict formats
                    if isinstance(data, list):
                        all_memes = data
                    elif isinstance(data, dict) and 'memes' in data:
                        all_memes = data['memes']
                    else:
                        all_memes = []
            except (FileNotFoundError, json.JSONDecodeError):
                all_memes = []
            
            # Sort memes if requested
            if sort_by == 'recent' and all_memes:
                # Sort by generated_at if available
                all_memes.sort(key=lambda x: x.get('generated_at', ''), reverse=True)
            
            return jsonify({
                'success': True,
                'memes': all_memes,
                'total_count': len(all_memes)
            })
            
        except Exception as e:
            print(f"Error getting memes: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/news')
    def get_news():
        """Get recent news articles for preview"""
        try:
            # Get duration from query params
            duration = int(request.args.get('duration', 1))
            
            # Use some default trends for news preview
            default_trends = ['AI', 'artificial intelligence', 'machine learning']
            
            articles = get_news_articles(default_trends, days_back=duration)
            
            # Format articles for frontend
            formatted_articles = []
            for article in articles[:10]:  # Limit to 10 for preview
                formatted_articles.append({
                    'title': article.get('title', ''),
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'published': article.get('publishedAt', ''),
                    'url': article.get('url', ''),
                    'description': article.get('description', '')[:500] + '...' if article.get('description') else ''
                })
            
            return jsonify({
                'success': True,
                'news': formatted_articles
            })
            
        except Exception as e:
            print(f"Error getting news: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/health')
    def health_check():
        """Health check endpoint for frontend"""
        return jsonify({
            'status': 'healthy',
            'service': 'AI Meme Factory',
            'timestamp': datetime.now().isoformat()
        })
    
    # Error handlers for better API responses
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'success': False, 'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'success': False, 'error': 'Internal server error'}), 500
    
    return app

if __name__ == '__main__':
    # Create database directory if it doesn't exist
    os.makedirs("database", exist_ok=True)
    
    app = create_app()
    print("\n" + "="*60)
    print("Starting AI Meme Factory...")
    print("="*60)
    
    # Show mode
    mode = "LOCAL (Stable Diffusion)" if args.local else "CLOUD (OpenAI)"
    print(f"\nMode: {mode}")
    
    # Check API keys based on mode
    print("\nRequired API Keys:")
    print(f"News API Key (FREE) configured: {'YES' if os.getenv('NEWS_API_KEY') and os.getenv('NEWS_API_KEY') != 'your-news-api-key-here' else 'NO'}")
    print(f"Gemini API Key (FREE) configured: {'YES' if os.getenv('GEMINI_API_KEY') and os.getenv('GEMINI_API_KEY') != 'your-gemini-key-here' else 'NO'}")
    
    if args.local:
        print("\nNote: Local mode uses Stable Diffusion for images")
    else:
        print(f"OpenAI API Key (PAID) configured: {'YES' if os.getenv('OPENAI_API_KEY') and os.getenv('OPENAI_API_KEY') != 'your-openai-key-here' else 'NO'}")
        print("\nNote: Cloud mode costs money per image generated")
    
    print("\nServer Info:")
    print("Templates folder: templates/")
    print("   - index.html (main page)")
    print("   - history.html (previous generations)")
    print("Static files folder: static/")
    print(f"Main page: http://localhost:{args.port}")
    print(f"History page: http://localhost:{args.port}/history")
    print("API endpoints:")
    print("   - POST /api/generate (generate memes)")
    print("   - GET  /api/memes (get existing memes)")
    print("   - GET  /api/news (get news preview)")
    print("   - GET  /api/health (health check)")
    
    # Check required API keys and warn if missing
    missing_keys = []
    
    # Always need news API and Gemini
    if not os.getenv('NEWS_API_KEY') or os.getenv('NEWS_API_KEY') == 'your-news-api-key-here':
        missing_keys.append('NEWS_API_KEY')
    
    if not os.getenv('GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY') == 'your-gemini-key-here':
        missing_keys.append('GEMINI_API_KEY')
    
    if not args.local:
        # Cloud mode also needs OpenAI
        if not os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY') == 'your-openai-key-here':
            missing_keys.append('OPENAI_API_KEY')
    
    if missing_keys:
        print("\n" + "!"*60)
        print("WARNING: Missing required API keys!")
        print("!"*60)
        print(f"\nMissing: {', '.join(missing_keys)}")
        print("\nThe app will start but meme generation will fail.")
        print("Please set these in your .env file.")
        print("\nGet your API keys here:")
        print("  NEWS_API_KEY: https://newsapi.org/ (FREE)")
        print("  GEMINI_API_KEY: https://aistudio.google.com/apikey (FREE)")
        if 'OPENAI_API_KEY' in missing_keys:
            print("  OPENAI_API_KEY: https://platform.openai.com/settings/organization/api-keys (PAID)")
        print("!"*60 + "\n")
    
    print("\n" + "="*60)
    print("Server starting...")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=args.port)