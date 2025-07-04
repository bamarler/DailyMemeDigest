# ==============================================================================
# FILE: app.py
# Main Flask application - entry point
# ==============================================================================

from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, session
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
    
    # Configure Flask secret key
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
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
    
    @app.route('/api/health')
    def health_check():
        """Health check endpoint for frontend"""
        return jsonify({
            'status': 'healthy',
            'service': 'AI Meme Factory',
            'timestamp': datetime.now().isoformat()
        })
    
    # Serve React build files (must be before catch-all route)
    @app.route('/static/css/<path:filename>')
    def serve_css(filename):
        """Serve CSS files from React build"""
        import os
        build_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'build')
        css_path = os.path.join(build_path, 'static', 'css')
        print(f"[DEBUG] Serving CSS file: {filename}")
        print(f"[DEBUG] CSS path: {css_path}")
        return send_from_directory(css_path, filename)
    
    @app.route('/static/js/<path:filename>')
    def serve_js(filename):
        """Serve JS files from React build"""
        import os
        build_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'build')
        js_path = os.path.join(build_path, 'static', 'js')
        print(f"[DEBUG] Serving JS file: {filename}")
        print(f"[DEBUG] JS path: {js_path}")
        return send_from_directory(js_path, filename)
    
    @app.route('/asset-manifest.json')
    def serve_asset_manifest():
        """Serve asset manifest from React build"""
        import os
        build_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'build')
        return send_from_directory(build_path, 'asset-manifest.json')
    
    @app.route('/favicon.ico')
    def serve_favicon():
        """Serve favicon from React build"""
        import os
        build_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'build')
        return send_from_directory(build_path, 'favicon.ico')
    
    @app.route('/api/subscribe', methods=['POST'])
    def api_subscribe():
        """Subscribe email to Mailchimp list"""
        try:
            data = request.get_json()
            email = data.get('email')
            print(f"[DEBUG] /api/subscribe called with email: {email}")
            
            if not email:
                print("[ERROR] No email provided to /api/subscribe")
                return jsonify({
                    'success': False,
                    'error': 'Email is required'
                }), 400
            
            # Initialize Mailchimp service
            try:
                from src.mailchimp_service import MailchimpService
                mailchimp = MailchimpService()
                print(f"[DEBUG] MailchimpService initialized in /api/subscribe")
                result = mailchimp.subscribe_email(email)
                print(f"[DEBUG] MailchimpService.subscribe_email result: {result}")
                
                return jsonify(result)
                
            except ImportError as e:
                print(f"[WARN] MailchimpService not available, simulating success. ImportError: {e}")
                # Fallback if Mailchimp is not configured
                return jsonify({
                    'success': True,
                    'message': 'Email subscription successful (Mailchimp not configured)'
                })
                
        except Exception as e:
            print(f"[ERROR] Exception in /api/subscribe: {e}")
            return jsonify({
                'success': False,
                'error': f'Subscription failed: {str(e)}'
            }), 500
    
    @app.route('/api/preferences', methods=['POST'])
    def api_preferences():
        """Update user preferences and send confirmation email"""
        try:
            data = request.get_json()
            email = data.get('email')
            preferences = data.get('preferences', {})
            print(f"[DEBUG] /api/preferences called with email: {email}, preferences: {preferences}")
            
            if not email:
                print("[ERROR] No email provided to /api/preferences")
                return jsonify({
                    'success': False,
                    'error': 'Email is required'
                }), 400
            
            # Initialize Mailchimp service
            try:
                from src.mailchimp_service import MailchimpService
                mailchimp = MailchimpService()
                print(f"[DEBUG] MailchimpService initialized in /api/preferences")
                result = mailchimp.update_preferences(email, preferences)
                print(f"[DEBUG] MailchimpService.update_preferences result: {result}")
                
                return jsonify(result)
                
            except ImportError as e:
                print(f"[WARN] MailchimpService not available, simulating success. ImportError: {e}")
                # Fallback if Mailchimp is not configured
                return jsonify({
                    'success': True,
                    'message': 'Preferences saved successfully (Mailchimp not configured)'
                })
                
        except Exception as e:
            print(f"[ERROR] Exception in /api/preferences: {e}")
            return jsonify({
                'success': False,
                'error': f'Failed to save preferences: {str(e)}'
            }), 500
    
    @app.route('/api/confirm/<token>')
    def api_confirm(token):
        """Confirm email subscription"""
        try:
            from src.mailchimp_service import MailchimpService
            mailchimp = MailchimpService()
            result = mailchimp.confirm_subscription(token)
            
            return jsonify(result)
            
        except ImportError:
            return jsonify({
                'success': True,
                'message': 'Subscription confirmed (Mailchimp not configured)'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Confirmation failed: {str(e)}'
            }), 500
    
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
    
    # Catch-all route for React Router (must be last)
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_react_app(path):
        """Serve React app for all routes"""
        import os
        build_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'build')
        return send_from_directory(build_path, 'index.html')
    
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
    print("Frontend: React app served from ../frontend/build/")
    print("Backend: Flask API server")
    print(f"Main page: http://localhost:{args.port}")
    print("API endpoints:")
    print("   - POST /api/generate (generate memes)")
    print("   - GET  /api/memes (get existing memes)")
    print("   - GET  /api/news (get news preview)")
    print("   - GET  /api/health (health check)")
    print("   - POST /api/subscribe (subscribe to Mailchimp list)")
    print("   - POST /api/preferences (update user preferences)")
    print("   - GET  /api/confirm/<token> (confirm email subscription)")
    
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