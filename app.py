# # ==============================================================================
# # FILE: app.py
# # Main Flask application - entry point
# # ==============================================================================

# from flask import Flask, render_template, request, jsonify
# import os
# import json
# from dotenv import load_dotenv

# # Load environment variables



# from src.news_aggregator import get_news_articles
# from src.filter_top_k import get_top_articles
# from src.prompt_generator import generate_meme_prompts
# from src.meme_generator import generate_meme_image

# load_dotenv()

# def create_app():
#     app = Flask(__name__)
#     # app.config.from_object(Config) 

#     @app.route('/')
#     def index():
#         """Serve the main HTML page"""
#         return render_template('index.html')
    
#     @app.route('/api/generate', methods=['POST'])
#     def generate_meme():
#         # Get JSON data from request body
#         data = request.get_json()
        
#         # Extract fields with defaults
#         trends = data.get('trends', [])  # List of keywords
#         duration = data.get('duration', 1)  # Days back, default to 1
        
#         # Call your methods with the extracted data
#         articles = get_news_articles(trends, days_back=duration)
#         top_articles = get_top_articles(articles, 1, trends)
#         prompts = generate_meme_prompts(top_articles)
#         print(prompts)
#         memes = generate_meme_image(prompts)

#         # Filter successful memes
#         parsed_memes = json.loads(memes)
#         successful_memes = [meme for meme in parsed_memes["memes"] if meme["success"]]
        
#         if successful_memes:
#             # Read existing memes
#             try:
#                 with open("database/memes.json", "r") as f:
#                     existing_memes = json.load(f)
#             except (FileNotFoundError, json.JSONDecodeError):
#                 existing_memes = []
            
#             # Append new memes
#             existing_memes.extend(successful_memes)
            
#             # Write back
#             with open("database/memes.json", "w") as f:
#                 json.dump(existing_memes, f, indent=2)
        
#         # Return the prompts as JSON
#         return jsonify(memes)
    
#     @app.route('/api/memes')
#     def get_memes():
#         with open("database/memes.json", "r") as f:
#             memes = json.load(f)
#         return jsonify(memes)
    
#     return app

# if __name__ == '__main__':
#     app = create_app()
#     print("🎭 Starting AI Meme Factory...")
#     print("🔑 Make sure to set your OPENAI_API_KEY and NEWS_API_KEY environment variables!")
#     print(os.getenv('NEWS_API_KEY'))
#     print(f"📰 News API Key configured: {'✅' if os.getenv('NEWS_API_KEY') != 'your-news-api-key-here' else '❌'}")
#     print(f"🤖 OpenAI API Key configured: {'✅' if os.getenv('OPENAI_API_KEY') != 'your-openai-key-here' else '❌'}")
#     print(f"🤖 Gemini API Key configured: {'✅' if os.getenv('GEMINI_API_KEY') != 'your-gemini-key-here' else '❌'}")
#     app.run(debug=True, host='0.0.0.0', port=5001)

# ==============================================================================
# FILE: app.py
# Main Flask application - entry point
# ==============================================================================

from flask import Flask, render_template, request, jsonify
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.news_aggregator import get_news_articles
from src.filter_top_k import get_top_articles
from src.prompt_generator import generate_meme_prompts
from src.meme_generator import generate_meme_image

def create_app():
    app = Flask(__name__)
    
    # Configure static files for the separated frontend
    app.static_folder = 'static'
    app.static_url_path = '/static'
    
    @app.route('/')
    def index():
        """Serve the main HTML page"""
        return render_template('index.html')
    
    @app.route('/api/generate', methods=['POST'])
    def generate_meme():
        """Generate memes based on user preferences"""
        try:
            print("🎲 Starting meme generation...")
            
            # Get JSON data from request body
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
            
            # Extract fields with defaults
            trends = data.get('trends', [])  # List of keywords
            duration = data.get('duration', 1)  # Days back, default to 1
            
            print(f"📊 Request: Trends={trends}, Duration={duration} days")
            
            if not trends:
                return jsonify({
                    'success': False,
                    'error': 'Please select at least one AI trend'
                }), 400
            
            # Call your methods with the extracted data
            print("📰 Fetching articles...")
            articles = get_news_articles(trends, days_back=duration)
            
            if not articles:
                return jsonify({
                    'success': False,
                    'error': 'No articles found for selected trends'
                })
            
            print(f"🎯 Filtering top articles from {len(articles)} total...")
            top_articles = get_top_articles(articles, 2, trends)
            
            print("💭 Generating prompts...")
            prompts = generate_meme_prompts(top_articles)
            print(f"Generated prompts: {prompts}")
            
            if not prompts:
                return jsonify({
                    'success': False,
                    'error': 'Failed to generate meme prompts'
                })
            
            print("🎨 Generating memes...")
            memes = generate_meme_image(prompts)
            
            # Handle both string and dict responses from generate_meme_image
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

            # Filter successful memes
            successful_memes = [meme for meme in parsed_memes["memes"] if meme.get("success", False)]
            
            print(f"✅ Generated {len(successful_memes)} successful memes")
            
            # Store successful memes
            if successful_memes:
                try:
                    # Create database directory if needed
                    os.makedirs("database", exist_ok=True)
                    
                    # Read existing memes
                    try:
                        with open("database/memes.json", "r") as f:
                            existing_memes = json.load(f)
                    except (FileNotFoundError, json.JSONDecodeError):
                        existing_memes = []
                    
                    # Add metadata to new memes
                    for meme in successful_memes:
                        meme['generated_at'] = datetime.now().isoformat()
                        meme['trends_used'] = trends
                        meme['duration_days'] = duration
                    
                    # Append new memes
                    existing_memes.extend(successful_memes)
                    
                    # Write back
                    with open("database/memes.json", "w") as f:
                        json.dump(existing_memes, f, indent=2)
                    
                    print(f"💾 Saved {len(successful_memes)} memes to database")
                    
                except Exception as e:
                    print(f"⚠️ Warning: Could not save memes: {e}")
            
            # Return the response in expected format
            if isinstance(memes, str):
                # If memes is JSON string, parse and return
                return memes, 200, {'Content-Type': 'application/json'}
            else:
                # If memes is dict, return as JSON
                return jsonify(memes)
                
        except Exception as e:
            print(f"❌ Error in meme generation: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Meme generation failed: {str(e)}'
            }), 500
    
    @app.route('/api/memes')
    def get_memes():
        """Get existing memes from database"""
        try:
            sort_by = request.args.get('sort', 'recent')
            limit = int(request.args.get('limit', 20))
            
            try:
                with open("database/memes.json", "r") as f:
                    all_memes = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                all_memes = []
            
            # Sort memes if requested
            if sort_by == 'recent' and all_memes:
                # Sort by generated_at if available
                all_memes.sort(key=lambda x: x.get('generated_at', ''), reverse=True)
            
            # Limit results
            memes = all_memes[:limit] if limit > 0 else all_memes
            
            return jsonify({
                'success': True,
                'memes': memes,
                'total_count': len(all_memes)
            })
            
        except Exception as e:
            print(f"❌ Error getting memes: {str(e)}")
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
                    'description': article.get('description', '')[:200] + '...' if article.get('description') else ''
                })
            
            return jsonify({
                'success': True,
                'news': formatted_articles
            })
            
        except Exception as e:
            print(f"❌ Error getting news: {str(e)}")
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
    print("🎭 Starting AI Meme Factory...")
    print("🔑 Make sure to set your API keys in environment variables!")
    
    # Debug: Print actual API key (first few chars only)
    news_key = os.getenv('NEWS_API_KEY')
    if news_key:
        print(f"📰 News API Key: {news_key[:10]}...")
    
    print(f"📰 News API Key configured: {'✅' if os.getenv('NEWS_API_KEY') != 'your-news-api-key-here' else '❌'}")
    print(f"🤖 OpenAI API Key configured: {'✅' if os.getenv('OPENAI_API_KEY') != 'your-openai-key-here' else '❌'}")
    print(f"🤖 Gemini API Key configured: {'✅' if os.getenv('GEMINI_API_KEY') != 'your-gemini-key-here' else '❌'}")
    
    print("\n🌐 Server Info:")
    print("📁 Templates folder: templates/")
    print("📁 Static files folder: static/")
    print("🎯 Main page: http://localhost:5001")
    print("🔌 API endpoints:")
    print("   - POST /api/generate (generate memes)")
    print("   - GET  /api/memes (get existing memes)")
    print("   - GET  /api/news (get news preview)")
    print("   - GET  /api/health (health check)")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
