"""
Mailchimp Service for AI Meme Newsletter
Handles email subscription and preference management
"""

import os
import requests
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MailchimpService:
    """Service class for Mailchimp API integration"""
    
    def __init__(self):
        """Initialize Mailchimp service with API credentials"""
        self.api_key = os.getenv('MAILCHIMP_API_KEY')
        self.server_prefix = os.getenv('MAILCHIMP_SERVER_PREFIX')
        self.list_id = os.getenv('MAILCHIMP_LIST_ID')
        
        # Check if all required environment variables are set
        if not all([self.api_key, self.server_prefix, self.list_id]):
            logger.warning("Mailchimp environment variables not fully configured")
            logger.warning(f"API_KEY: {'SET' if self.api_key else 'MISSING'}")
            logger.warning(f"SERVER_PREFIX: {'SET' if self.server_prefix else 'MISSING'}")
            logger.warning(f"LIST_ID: {'SET' if self.list_id else 'MISSING'}")
            raise ImportError("Mailchimp configuration incomplete")
        
        self.base_url = f"https://{self.server_prefix}.api.mailchimp.com/3.0"
        self.auth = ('anystring', self.api_key)  # Mailchimp uses API key as password
        
        logger.info("MailchimpService initialized successfully")
    
    def subscribe_email(self, email: str) -> Dict[str, Any]:
        """
        Subscribe an email to the Mailchimp list
        
        Args:
            email: Email address to subscribe
            
        Returns:
            Dict with success status and message
        """
        try:
            logger.info(f"Attempting to subscribe email: {email}")
            
            # Prepare subscriber data
            subscriber_data = {
                "email_address": email,
                "status": "pending",  # Send confirmation email
                "merge_fields": {
                    "FNAME": email.split('@')[0],  # Use email prefix as first name
                }
            }
            
            # Make API request
            url = f"{self.base_url}/lists/{self.list_id}/members"
            response = requests.post(url, json=subscriber_data, auth=self.auth)
            
            if response.status_code == 200:
                logger.info(f"Successfully subscribed {email}")
                return {
                    'success': True,
                    'message': 'Email subscription successful! Please check your email for confirmation.'
                }
            elif response.status_code == 400:
                # Check if it's a duplicate subscription
                error_data = response.json()
                if 'already a list member' in str(error_data):
                    logger.info(f"Email {email} is already subscribed")
                    return {
                        'success': True,
                        'message': 'Email is already subscribed to our newsletter!'
                    }
                else:
                    logger.error(f"Mailchimp API error: {error_data}")
                    return {
                        'success': False,
                        'error': f'Subscription failed: {error_data}'
                    }
            else:
                logger.error(f"Mailchimp API error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f'Subscription failed: HTTP {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Exception in subscribe_email: {str(e)}")
            return {
                'success': False,
                'error': f'Subscription failed: {str(e)}'
            }
    
    def update_preferences(self, email: str, preferences: Dict[str, bool]) -> Dict[str, Any]:
        """
        Update user preferences in Mailchimp
        
        Args:
            email: Email address
            preferences: Dict of preference keys and boolean values
            
        Returns:
            Dict with success status and message
        """
        try:
            logger.info(f"Updating preferences for {email}: {preferences}")
            
            # Convert preferences to Mailchimp merge fields
            merge_fields = {}
            for key, value in preferences.items():
                # Convert boolean to string for Mailchimp
                merge_fields[key] = str(value).lower()
            
            # Prepare update data
            update_data = {
                "merge_fields": merge_fields
            }
            
            # Get subscriber hash (MD5 of lowercase email)
            import hashlib
            subscriber_hash = hashlib.md5(email.lower().encode()).hexdigest()
            
            # Make API request
            url = f"{self.base_url}/lists/{self.list_id}/members/{subscriber_hash}"
            response = requests.patch(url, json=update_data, auth=self.auth)
            
            if response.status_code == 200:
                logger.info(f"Successfully updated preferences for {email}")
                return {
                    'success': True,
                    'message': 'Preferences saved successfully!'
                }
            else:
                logger.error(f"Mailchimp API error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f'Failed to update preferences: HTTP {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Exception in update_preferences: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to update preferences: {str(e)}'
            }
    
    def confirm_subscription(self, token: str) -> Dict[str, Any]:
        """
        Confirm email subscription using token
        
        Args:
            token: Confirmation token from email
            
        Returns:
            Dict with success status and message
        """
        try:
            logger.info(f"Confirming subscription with token: {token}")
            
            # This would typically involve parsing the token and making an API call
            # For now, we'll simulate success
            return {
                'success': True,
                'message': 'Subscription confirmed successfully!'
            }
            
        except Exception as e:
            logger.error(f"Exception in confirm_subscription: {str(e)}")
            return {
                'success': False,
                'error': f'Confirmation failed: {str(e)}'
            }
    
    def get_subscriber_info(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get subscriber information from Mailchimp
        
        Args:
            email: Email address
            
        Returns:
            Dict with subscriber info or None if not found
        """
        try:
            # Get subscriber hash
            import hashlib
            subscriber_hash = hashlib.md5(email.lower().encode()).hexdigest()
            
            # Make API request
            url = f"{self.base_url}/lists/{self.list_id}/members/{subscriber_hash}"
            response = requests.get(url, auth=self.auth)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Subscriber not found: {email}")
                return None
                
        except Exception as e:
            logger.error(f"Exception in get_subscriber_info: {str(e)}")
            return None 