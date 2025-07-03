# ==============================================================================
# FILE: src/mailchimp_service.py
# Mailchimp API integration for email subscriptions
# ==============================================================================

import os
import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError
from typing import Dict, List, Optional

class MailchimpService:
    """
    Service class for handling Mailchimp API operations.
    
    Handles email subscriptions, preference updates, and confirmation emails.
    """
    
    def __init__(self):
        """
        Initialize Mailchimp service with API credentials.
        
        Requires environment variables:
        - MAILCHIMP_API_KEY: Your Mailchimp API key
        - MAILCHIMP_SERVER_PREFIX: Your Mailchimp server prefix (e.g., 'us1')
        - MAILCHIMP_LIST_ID: Your Mailchimp audience/list ID
        """
        self.api_key = os.getenv('MAILCHIMP_API_KEY')
        self.server_prefix = os.getenv('MAILCHIMP_SERVER_PREFIX')
        self.list_id = os.getenv('MAILCHIMP_LIST_ID')
        
        if not all([self.api_key, self.server_prefix, self.list_id]):
            raise ValueError("Missing required Mailchimp environment variables")
        
        self.client = MailchimpMarketing.Client()
        self.client.set_config({
            "api_key": self.api_key,
            "server": self.server_prefix
        })
    
    def subscribe_email(self, email: str) -> Dict:
        """
        Subscribe an email address to the Mailchimp list.
        
        Input:
            email (str): Email address to subscribe
            
        Output:
            Dict: Response with success status and message
        """
        try:
            response = self.client.lists.add_list_member(self.list_id, {
                "email_address": email,
                "status": "subscribed",
                "merge_fields": {
                    "FNAME": "",
                    "LNAME": ""
                }
            })
            
            return {
                "success": True,
                "message": "Successfully subscribed to newsletter",
                "subscriber_hash": response.get("id")
            }
            
        except ApiClientError as error:
            error_text = error.text
            if "Member Exists" in error_text:
                return {
                    "success": True,
                    "message": "Email already subscribed",
                    "subscriber_hash": None
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to subscribe: {error_text}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def update_preferences(self, email: str, preferences: Dict) -> Dict:
        """
        Update user preferences and send confirmation email.
        
        Input:
            email (str): Email address of the subscriber
            preferences (Dict): Dictionary of news category preferences
            
        Output:
            Dict: Response with success status and message
        """
        try:
            # Get subscriber hash
            subscriber_hash = self._get_subscriber_hash(email)
            if not subscriber_hash:
                return {
                    "success": False,
                    "error": "Subscriber not found"
                }
            
            # Update merge fields with preferences
            merge_fields = {}
            for category, enabled in preferences.items():
                merge_fields[f"PREF_{category.upper()}"] = "Yes" if enabled else "No"
            
            # Update subscriber
            self.client.lists.set_list_member(self.list_id, subscriber_hash, {
                "merge_fields": merge_fields
            })
            
            # Send confirmation email
            self._send_confirmation_email(subscriber_hash)
            
            return {
                "success": True,
                "message": "Preferences updated and confirmation email sent"
            }
            
        except ApiClientError as error:
            return {
                "success": False,
                "error": f"Failed to update preferences: {error.text}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def _get_subscriber_hash(self, email: str) -> Optional[str]:
        """
        Get subscriber hash from email address.
        
        Input:
            email (str): Email address to look up
            
        Output:
            Optional[str]: Subscriber hash if found, None otherwise
        """
        try:
            response = self.client.lists.get_list_member(self.list_id, email)
            return response.get("id")
        except ApiClientError:
            return None
    
    def _send_confirmation_email(self, subscriber_hash: str) -> bool:
        """
        Send confirmation email to subscriber.
        
        Input:
            subscriber_hash (str): Mailchimp subscriber hash
            
        Output:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # This would typically use Mailchimp's automation or campaign API
            # For now, we'll just return True as a placeholder
            # In a real implementation, you'd trigger an automation or send a campaign
            return True
        except Exception:
            return False
    
    def confirm_subscription(self, token: str) -> Dict:
        """
        Confirm email subscription using token from confirmation link.
        
        Input:
            token (str): Confirmation token from email link
            
        Output:
            Dict: Response with success status and message
        """
        try:
            # This would validate the token and confirm the subscription
            # For now, we'll return success as a placeholder
            return {
                "success": True,
                "message": "Subscription confirmed successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to confirm subscription: {str(e)}"
            } 