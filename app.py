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
    
    @app.route('/debug/mailerlite')
    def debug_mailerlite():
        """
        Debug endpoint to check MailerLite configuration (no sensitive data)
        
        Returns:
            JSON response with configuration status
        """
        mailerlite_api_key = os.getenv('MAILERLITE_API_KEY')
        mailerlite_group_id = os.getenv('MAILERLITE_GROUP_ID')
        
        # Test MailerLite connection
        connection_test = "Not tested"
        try:
            if all([mailerlite_api_key, mailerlite_group_id]):
                headers = {
                    'Authorization': f'Bearer {mailerlite_api_key}',
                    'Content-Type': 'application/json'
                }
                
                # Test by getting account info
                response = requests.get('https://connect.mailerlite.com/api/account', headers=headers)
                if response.status_code == 200:
                    account_info = response.json()
                    connection_test = f"✅ Connected - Account: {account_info.get('data', {}).get('name', 'Unknown')}"
                else:
                    connection_test = f"❌ Connection failed: {response.status_code}"
            else:
                connection_test = "❌ Missing configuration"
        except Exception as e:
            connection_test = f"❌ Connection failed: {str(e)}"
        
        return jsonify({
            'mailerlite_configured': bool(all([mailerlite_api_key, mailerlite_group_id])),
            'api_key_set': bool(mailerlite_api_key),
            'group_id_set': bool(mailerlite_group_id),
            'group_id': mailerlite_group_id if mailerlite_group_id else None,
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
        Subscribe email to newsletter via MailerLite
        
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
            
            # Get MailerLite configuration from environment with debugging
            mailerlite_api_key = os.getenv('MAILERLITE_API_KEY')
            mailerlite_group_id = os.getenv('MAILERLITE_GROUP_ID')
            
            # Debug logging for MailerLite configuration
            app.logger.info("=== MailerLite Configuration Debug ===")
            app.logger.info(f"MAILERLITE_API_KEY: {'✓ Set' if mailerlite_api_key else '✗ Missing'}")
            app.logger.info(f"MAILERLITE_GROUP_ID: {'✓ Set' if mailerlite_group_id else '✗ Missing'}")
            
            if mailerlite_api_key:
                app.logger.info(f"API Key starts with: {mailerlite_api_key[:10]}...")
            if mailerlite_group_id:
                app.logger.info(f"Group ID: {mailerlite_group_id}")
            
            if not all([mailerlite_api_key, mailerlite_group_id]):
                missing_vars = []
                if not mailerlite_api_key:
                    missing_vars.append("MAILERLITE_API_KEY")
                if not mailerlite_group_id:
                    missing_vars.append("MAILERLITE_GROUP_ID")
                
                app.logger.error(f"MailerLite configuration missing: {', '.join(missing_vars)}")
                return jsonify({
                    'success': False,
                    'error': f'Newsletter service not configured. Missing: {", ".join(missing_vars)}'
                }), 500
            
            # Set up MailerLite API headers
            headers = {
                'Authorization': f'Bearer {mailerlite_api_key}',
                'Content-Type': 'application/json'
            }
            
            # Add subscriber to MailerLite group
            try:
                # Check if subscriber already exists
                try:
                    response = requests.get(
                        f'https://connect.mailerlite.com/api/subscribers/{email}',
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        # Subscriber already exists, check if they're in the group
                        subscriber_data = response.json()
                        app.logger.info(f"Subscriber already exists: {email}")
                        
                        # Check if subscriber is in our group
                        group_response = requests.get(
                            f'https://connect.mailerlite.com/api/groups/{mailerlite_group_id}/subscribers/{email}',
                            headers=headers
                        )
                        
                        if group_response.status_code == 200:
                            return jsonify({
                                'success': True,
                                'message': 'You are already subscribed to our newsletter!'
                            })
                        else:
                            # Subscriber exists but not in group, add them
                            app.logger.info(f"Subscriber exists but not in group, adding to group: {email}")
                    elif response.status_code == 404:
                        # Subscriber doesn't exist, create them
                        app.logger.info(f"Subscriber doesn't exist, creating: {email}")
                    else:
                        app.logger.error(f"Unexpected response checking subscriber: {response.status_code}")
                        raise Exception(f"Failed to check subscriber: {response.status_code}")
                        
                except requests.exceptions.RequestException as e:
                    app.logger.error(f"Request error checking subscriber: {str(e)}")
                    raise e
                
                # Add new subscriber to group
                subscriber_data = {
                    "email": email,
                    "status": "active",
                    "groups": [mailerlite_group_id],
                    "fields": {
                        "name": email.split('@')[0]  # Use part before @ as first name
                    }
                }
                
                app.logger.info(f"Attempting to add subscriber with data: {subscriber_data}")
                
                # Create or update subscriber
                response = requests.post(
                    'https://connect.mailerlite.com/api/subscribers',
                    headers=headers,
                    json=subscriber_data
                )
                
                if response.status_code in [200, 201]:  # Both 200 and 201 indicate success
                    result = response.json()
                    app.logger.info(f"MailerLite API response: {result}")
                    app.logger.info(f"Successfully added subscriber: {email}")
                    return jsonify({
                        'success': True,
                        'message': 'Successfully subscribed to newsletter!'
                    })
                else:
                    app.logger.error(f"MailerLite API error: Status {response.status_code}, Response: {response.text}")
                    if response.status_code == 400:
                        return jsonify({
                            'success': False,
                            'error': 'Invalid email address or already subscribed'
                        }), 400
                    elif response.status_code == 401:
                        app.logger.error("MailerLite authentication failed - check API key")
                        return jsonify({
                            'success': False,
                            'error': 'Newsletter service authentication failed'
                        }), 500
                    elif response.status_code == 404:
                        app.logger.error("MailerLite group not found - check GROUP_ID")
                        return jsonify({
                            'success': False,
                            'error': 'Newsletter group not found'
                        }), 500
                    else:
                        app.logger.error(f"Unexpected MailerLite error: {response.status_code} - {response.text}")
                        return jsonify({
                            'success': False,
                            'error': 'Failed to subscribe. Please try again later.'
                        }), 500
                
            except requests.exceptions.RequestException as e:
                app.logger.error(f"Request error in subscription: {str(e)}")
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
    # Only build frontend in development
    if os.getenv('ENVIRONMENT', 'development') == 'development':
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
    print(f"MailerLite: {'✓' if os.getenv('MAILERLITE_API_KEY') else '✗'}")
    
    print("\nEndpoints:")
    print("  GET  /                    - React Frontend")
    print("  GET  /health              - Health Check")
    print("  GET  /debug/mailerlite    - MailerLite Configuration Debug")
    print("  GET  /memes               - Get Memes")
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