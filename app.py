"""
Simplified Flask application for AI Meme Newsletter
Uses DailyMemeDigest API for functionality
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import requests

load_dotenv()

from mailchimp_marketing import Client
from mailchimp_marketing.api_client import ApiClientError

def create_app():
    """
    Create and configure the simplified Flask application
    
    Returns:
        Flask app instance configured for newsletter functionality
    """
    app = Flask(__name__)
    
    # Configure CORS
    allowed_origins = os.getenv('ALLOWED_ORIGINS', '*').split(',')
    CORS(app, origins=allowed_origins)
    
    # DailyMemeDigest API configuration
    DAILYMEMEDIGEST_API_URL = os.getenv('DAILYMEMEDIGEST_API_URL', 'https://api.dailymemedigest.com')
    DAILYMEMEDIGEST_API_KEY = os.getenv('DAILYMEMEDIGEST_API_KEY')
    
    @app.route('/api/v1/health')
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
    
    @app.route('/api/v1/debug/mailchimp')
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
    
    @app.route('/api/v1/memes', methods=['GET'])
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
                headers['Authorization'] = f'Bearer {DAILYMEMEDIGEST_API_KEY}'
            
            params = {
                'limit': limit,
                'offset': offset
            }
            
            response = requests.get(
                f"{DAILYMEMEDIGEST_API_URL}/api/v1/memes",
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

if __name__ == '__main__':
    app = create_app()
    
    print("\n" + "="*60)
    print("AI Meme Newsletter API Server")
    print("="*60)
    
    print("\nAPI Configuration:")
    print(f"Version: 1.0.0")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"CORS Origins: {os.getenv('ALLOWED_ORIGINS', '*')}")
    
    print("\nExternal Services:")
    print(f"DailyMemeDigest API: {'✓' if os.getenv('DAILYMEMEDIGEST_API_KEY') else '✗'}")
    print(f"Mailchimp: {'✓' if os.getenv('MAILCHIMP_API_KEY') else '✗'}")
    
    print("\nEndpoints:")
    print("  GET  /api/v1/health")
    print("  GET  /api/v1/debug/mailchimp (no API key required)")
    print("  GET  /api/v1/memes (no API key required)")
    print("  POST /api/subscribe (no API key required)")
    
    print("\n" + "="*60 + "\n")
    
    port = int(os.getenv('PORT', 8080))
    debug = os.getenv('ENVIRONMENT', 'development') == 'development'
    
    app.run(debug=debug, host='0.0.0.0', port=port)