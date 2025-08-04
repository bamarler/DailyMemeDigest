"""
Unified Flask application for AI Meme Newsletter
Serves both API and React frontend
"""

from flask import Flask, request, jsonify, Response, send_from_directory, render_template
from flask_cors import CORS
import os
import json
import subprocess
import sys
from datetime import datetime
from dotenv import load_dotenv
import requests
from pathlib import Path

load_dotenv()

from mailchimp_marketing import Client
from mailchimp_marketing.api_client import ApiClientError

def create_app():
    """
    Create and configure the unified Flask application
    
    Returns:
        Flask app instance configured for newsletter functionality and frontend serving
    """
    app = Flask(__name__, static_folder='frontend/build', static_url_path='')
    
    # Configure CORS
    allowed_origins = os.getenv('ALLOWED_ORIGINS', '*').split(',')
    CORS(app, origins=allowed_origins)
    
    # DailyMemeDigest API configuration
    DAILYMEMEDIGEST_API_URL = os.getenv('DAILYMEMEDIGEST_API_URL', 'https://api.dailymemedigest.com')
    DAILYMEMEDIGEST_API_KEY = os.getenv('DAILYMEMEDIGEST_API_KEY')
    
    @app.route('/')
    def index():
        """Serve the React frontend"""
        return send_from_directory('frontend/build', 'index.html')
    
    @app.route('/<path:path>')
    def serve_static(path):
        """Serve static files from the React build"""
        if os.path.exists(os.path.join('frontend/build', path)):
            return send_from_directory('frontend/build', path)
        else:
            return send_from_directory('frontend/build', 'index.html')
    
    @app.route('/health')
    def health_check():
        """
        Health check endpoint for monitoring
        
        Returns:
            JSON response with service status
        """
        return jsonify({
            'status': 'healthy',
            'service': 'AI Meme Newsletter API',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat()
        })
    
    @app.route('/debug/mailchimp')
    def debug_mailchimp():
        """
        Debug endpoint to check Mailchimp configuration (no sensitive data)
        
        Returns:
            JSON response with configuration status
        """
        mailchimp_api_key = os.getenv('MAILCHIMP_API_KEY')
        mailchimp_server_prefix = os.getenv('MAILCHIMP_SERVER_PREFIX')
        mailchimp_list_id = os.getenv('MAILCHIMP_LIST_ID')
        
        # Test Mailchimp connection
        connection_test = "Not tested"
        try:
            if all([mailchimp_api_key, mailchimp_server_prefix, mailchimp_list_id]):
                mailchimp = Client()
                mailchimp.set_config({
                    "api_key": mailchimp_api_key,
                    "server": mailchimp_server_prefix
                })
                
                # Test by getting list info
                list_info = mailchimp.lists.get_list(list_id=mailchimp_list_id)
                connection_test = f"✅ Connected - List: {list_info.get('name', 'Unknown')}"
            else:
                connection_test = "❌ Missing configuration"
        except Exception as e:
            connection_test = f"❌ Connection failed: {str(e)}"
        
        return jsonify({
            'mailchimp_configured': bool(all([mailchimp_api_key, mailchimp_server_prefix, mailchimp_list_id])),
            'api_key_set': bool(mailchimp_api_key),
            'server_prefix_set': bool(mailchimp_server_prefix),
            'list_id_set': bool(mailchimp_list_id),
            'server_prefix': mailchimp_server_prefix if mailchimp_server_prefix else None,
            'list_id': mailchimp_list_id if mailchimp_list_id else None,
            'connection_test': connection_test
        })
    
    @app.route('/memes', methods=['GET'])
    def get_memes():
        """
        Get memes from DailyMemeDigest API
        
        Parameters:
            - limit (int): Number of memes to return (default 30, max 100)
            - offset (int): Number of memes to skip (default 0)
            
        Returns:
            JSON response with paginated memes
        """
        try:
            # Parse query parameters
            limit = int(request.args.get('limit', 30))
            offset = int(request.args.get('offset', 0))
            
            # Validate parameters
            if limit > 100:
                return jsonify({
                    'success': False,
                    'error': 'Limit cannot exceed 100'
                }), 400
            
            # Call DailyMemeDigest API
            headers = {}
            if DAILYMEMEDIGEST_API_KEY:
                headers['X-API-Key'] = DAILYMEMEDIGEST_API_KEY
            
            params = {
                'limit': limit,
                'offset': offset
            }
            
            response = requests.get(
                f"{DAILYMEMEDIGEST_API_URL}/memes",
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                return jsonify(response.json())
            else:
                app.logger.error(f"DailyMemeDigest API error: {response.status_code} - {response.text}")
                return jsonify({
                    'success': False,
                    'error': 'Failed to fetch memes from external API'
                }), 500
                
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': 'Invalid parameter values'
            }), 400
        except Exception as e:
            app.logger.error(f"Error getting memes: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Internal server error'
            }), 500
    
    @app.route('/api/subscribe', methods=['POST'])
    def subscribe():
        """
        Subscribe email to newsletter via Mailchimp (no API key required)
        
        Returns:
            JSON response with subscription status
        """
        try:
            data = request.get_json()
            
            if not data or 'email' not in data:
                return jsonify({
                    'success': False,
                    'error': 'Email is required'
                }), 400
            
            email = data['email'].strip().lower()
            
            # Basic email validation
            import re
            email_pattern = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
            if not email_pattern.match(email):
                return jsonify({
                    'success': False,
                    'error': 'Invalid email format'
                }), 400
            
            # Get Mailchimp configuration from environment with debugging
            mailchimp_api_key = os.getenv('MAILCHIMP_API_KEY')
            mailchimp_server_prefix = os.getenv('MAILCHIMP_SERVER_PREFIX')
            mailchimp_list_id = os.getenv('MAILCHIMP_LIST_ID')
            
            # Debug logging for Mailchimp configuration
            app.logger.info("=== Mailchimp Configuration Debug ===")
            app.logger.info(f"MAILCHIMP_API_KEY: {'✓ Set' if mailchimp_api_key else '✗ Missing'}")
            app.logger.info(f"MAILCHIMP_SERVER_PREFIX: {'✓ Set' if mailchimp_server_prefix else '✗ Missing'}")
            app.logger.info(f"MAILCHIMP_LIST_ID: {'✓ Set' if mailchimp_list_id else '✗ Missing'}")
            
            if mailchimp_api_key:
                app.logger.info(f"API Key starts with: {mailchimp_api_key[:10]}...")
            if mailchimp_server_prefix:
                app.logger.info(f"Server prefix: {mailchimp_server_prefix}")
            if mailchimp_list_id:
                app.logger.info(f"List ID: {mailchimp_list_id}")
            
            if not all([mailchimp_api_key, mailchimp_server_prefix, mailchimp_list_id]):
                missing_vars = []
                if not mailchimp_api_key:
                    missing_vars.append("MAILCHIMP_API_KEY")
                if not mailchimp_server_prefix:
                    missing_vars.append("MAILCHIMP_SERVER_PREFIX")
                if not mailchimp_list_id:
                    missing_vars.append("MAILCHIMP_LIST_ID")
                
                app.logger.error(f"Mailchimp configuration missing: {', '.join(missing_vars)}")
                return jsonify({
                    'success': False,
                    'error': f'Newsletter service not configured. Missing: {", ".join(missing_vars)}'
                }), 500
            
            # Initialize Mailchimp client
            mailchimp = Client()
            mailchimp.set_config({
                "api_key": mailchimp_api_key,
                "server": mailchimp_server_prefix
            })
            
            # Add subscriber to Mailchimp list
            try:
                # Check if subscriber already exists
                try:
                    subscriber_hash = mailchimp.lists.get_list_member(
                        list_id=mailchimp_list_id,
                        subscriber_hash=email
                    )
                    # Subscriber already exists
                    app.logger.info(f"Subscriber already exists: {email}")
                    return jsonify({
                        'success': True,
                        'message': 'You are already subscribed to our newsletter!'
                    })
                except ApiClientError as e:
                    if e.status_code == 404:
                        # Subscriber doesn't exist, add them
                        pass
                    else:
                        raise e
                
                # Add new subscriber
                subscriber_data = {
                    "email_address": email,
                    "status": "subscribed",
                    "merge_fields": {
                        "FNAME": email.split('@')[0]  # Use part before @ as first name
                    }
                }
                
                app.logger.info(f"Attempting to add subscriber with data: {subscriber_data}")
                
                result = mailchimp.lists.add_list_member(
                    list_id=mailchimp_list_id,
                    body=subscriber_data
                )
                
                app.logger.info(f"Mailchimp API response: {result}")
                app.logger.info(f"Successfully added subscriber: {email}")
                return jsonify({
                    'success': True,
                    'message': 'Successfully subscribed to newsletter!'
                })
                
            except ApiClientError as e:
                app.logger.error(f"Mailchimp API error: Status {e.status_code}, Response: {e.text}")
                if e.status_code == 400:
                    app.logger.error(f"Bad request error: {e.text}")
                    return jsonify({
                        'success': False,
                        'error': 'Invalid email address or already subscribed'
                    }), 400
                elif e.status_code == 401:
                    app.logger.error("Mailchimp authentication failed - check API key")
                    return jsonify({
                        'success': False,
                        'error': 'Newsletter service authentication failed'
                    }), 500
                elif e.status_code == 404:
                    app.logger.error("Mailchimp list not found - check LIST_ID")
                    return jsonify({
                        'success': False,
                        'error': 'Newsletter list not found'
                    }), 500
                else:
                    app.logger.error(f"Unexpected Mailchimp error: {e.status_code} - {e.text}")
                    return jsonify({
                        'success': False,
                        'error': 'Failed to subscribe. Please try again later.'
                    }), 500
            
        except Exception as e:
            app.logger.error(f"Error in subscription: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Internal server error'
            }), 500


    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors"""
        return jsonify({'success': False, 'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        return jsonify({'success': False, 'error': 'Internal server error'}), 500
    
    @app.errorhandler(429)
    def rate_limit_error(error):
        """Handle rate limit errors"""
        return jsonify({'success': False, 'error': 'Rate limit exceeded'}), 429
    
    return app

def build_frontend():
    """Build the React frontend if it doesn't exist or is outdated"""
    frontend_dir = Path('frontend')
    build_dir = frontend_dir / 'build'
    
    # Check if build directory exists and has content
    if not build_dir.exists() or not any(build_dir.iterdir()):
        print("🔨 Building React frontend...")
        try:
            # Store current directory
            current_dir = os.getcwd()
            
            # Change to frontend directory
            os.chdir(frontend_dir)
            print(f"📁 Changed to directory: {os.getcwd()}")
            
            # Install dependencies if node_modules doesn't exist
            if not Path('node_modules').exists():
                print("📦 Installing dependencies...")
                result = subprocess.run(['npm', 'install'], capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"❌ npm install failed: {result.stderr}")
                    os.chdir(current_dir)
                    return False
                print("✅ Dependencies installed")
            
            # Build the React app
            print("🏗️  Building React app...")
            result = subprocess.run(['npm', 'run', 'build'], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ npm run build failed: {result.stderr}")
                os.chdir(current_dir)
                return False
            
            # Change back to root directory
            os.chdir(current_dir)
            print(f"📁 Changed back to directory: {os.getcwd()}")
            
            print("✅ Frontend built successfully!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to build frontend: {e}")
            print(f"Error output: {e.stderr}")
            return False
        except Exception as e:
            print(f"❌ Error building frontend: {e}")
            return False
    else:
        print("✅ Frontend build already exists")
        return True
        
app = create_app()

if __name__ == '__main__':
    # Build frontend first
    if not build_frontend():
        print("❌ Failed to build frontend. Exiting.")
        sys.exit(1)
    
    
    
    print("\n" + "="*60)
    print("AI Meme Newsletter - Unified Server")
    print("="*60)
    
    print("\nServer Configuration:")
    print(f"Version: 1.0.0")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"CORS Origins: {os.getenv('ALLOWED_ORIGINS', '*')}")
    
    print("\nExternal Services:")
    print(f"DailyMemeDigest API: {'✓' if os.getenv('DAILYMEMEDIGEST_API_KEY') else '✗'}")
    print(f"Mailchimp: {'✓' if os.getenv('MAILCHIMP_API_KEY') else '✗'}")
    
    print("\nEndpoints:")
    print("  GET  /                    - React Frontend")
    print("  GET  /health       - Health Check")
    print("  GET  /debug/mailchimp")
    print("  GET  /memes        - Get Memes")
    print("  POST /api/subscribe       - Subscribe to Newsletter")
    
    print("\n" + "="*60 + "\n")
    
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('ENVIRONMENT', 'development') == 'development'
    
    print(f"🚀 Server starting on http://localhost:{port}")
    print("📱 Frontend will be available at the same URL")
    print("🔧 API endpoints available at /api/*")
    
    try:
        app.run(debug=debug, host='0.0.0.0', port=port)
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)