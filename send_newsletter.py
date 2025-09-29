#!/usr/bin/env python3
"""
DailyMemeDigest Newsletter Sender - CORRECTED VERSION
Sends automated newsletters using Brevo API (New Version)
"""

import os
import requests
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def debug_print(message):
    """Print debug messages with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_brevo_connection():
    """Test Brevo API connection by listing lists and account info"""
    debug_print("🔌 Testing Brevo connection...")
    
    api_key = os.getenv('BREVO_API_KEY')
    if not api_key:
        debug_print("❌ BREVO_API_KEY not found in environment")
        return False
    
    headers = {
        'api-key': api_key,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    try:
        # Test connection by listing lists (this confirms API key works)
        response = requests.get('https://api.brevo.com/v3/contacts/lists', headers=headers, timeout=10)
        debug_print(f"📡 Lists API Response: {response.status_code}")
        
        if response.status_code == 200:
            lists_data = response.json()
            list_count = len(lists_data.get('lists', []))
            debug_print(f"✅ Connected to Brevo successfully! Found {list_count} lists in account")
            
            # Also get account info to check sender email
            account_response = requests.get('https://api.brevo.com/v3/account', headers=headers, timeout=10)
            if account_response.status_code == 200:
                account_data = account_response.json()
                account_name = account_data.get('email', 'Unknown')
                debug_print(f"📧 Account: {account_name}")
                
                # Check if from email is verified
                from_email = os.getenv('BREVO_FROM_EMAIL')
                if from_email:
                    debug_print(f"📧 From email: {from_email}")
                    debug_print("⚠️  Make sure this email is verified in your Brevo account!")
                
            return True
        else:
            debug_print(f"❌ Connection failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        debug_print(f"❌ Connection error: {str(e)}")
        return False

def get_list_info():
    """Get information about the subscriber list"""
    debug_print("📊 Getting list information...")
    
    api_key = os.getenv('BREVO_API_KEY')
    list_id = os.getenv('BREVO_LIST_ID')
    
    if not list_id:
        debug_print("❌ BREVO_LIST_ID not found in environment")
        return None
    
    headers = {
        'api-key': api_key,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.get(
            f'https://api.brevo.com/v3/contacts/lists/{list_id}',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            list_data = response.json()
            list_name = list_data.get('name', 'Unknown')
            subscriber_count = list_data.get('uniqueSubscribers', 0)
            debug_print(f"✅ List: {list_name} ({subscriber_count} active subscribers)")
            return list_data
        else:
            debug_print(f"❌ Failed to get list info: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        debug_print(f"❌ Error getting list info: {str(e)}")
        return None

def create_newsletter_content(memes):
    """Create newsletter content with welcome message"""
    debug_print("📝 Creating welcome newsletter content...")
    
    # Create HTML content with proper unsubscribe link
    html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>Welcome to Daily Meme Digest!</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
        <h1 style="margin: 0; font-size: 28px;">Welcome to Daily Meme Digest! 🎉</h1>
    </div>
    
    <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
        <p style="font-size: 18px; margin-bottom: 20px;">Hey there, meme lover!</p>
        
        <p>Thanks for subscribing to Daily Meme Digest! We're excited to have you on board.</p>
        
        <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="color: #667eea; margin-top: 0;">What's coming soon:</h3>
            <ul style="padding-left: 20px;">
                <li>🎭 Fresh memes delivered daily</li>
                <li>📱 Mobile-friendly newsletter</li>
                <li>🎯 Curated content just for you</li>
                <li>🚀 Early access to new features</li>
            </ul>
        </div>
        
        <p>We're currently setting up our meme pipeline to bring you the best content every day. Stay tuned for the first batch of memes coming soon!</p>
        
        <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="color: #667eea; margin-top: 0;">In the meantime, you can:</h3>
            <ul style="padding-left: 20px;">
                <li>📧 Check your email preferences</li>
                <li>🌐 Visit our website for updates</li>
                <li>📱 Follow us on social media</li>
            </ul>
        </div>
        
        <p>Thanks for being part of our meme community!</p>
        
        <p style="margin-top: 30px;">
            <strong>Best regards,<br>
            The Daily Meme Digest Team</strong>
        </p>
        
        <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
        <p style="font-size: 12px; color: #666; text-align: center;">
            You're receiving this because you subscribed to Daily Meme Digest.<br>
            <a href="https://dailymemedigest.com" style="color: #667eea;">Visit our website</a> | 
            <a href="{$unsubscribe}" style="color: #667eea;">Unsubscribe</a>
        </p>
    </div>
</body>
</html>'''
    
    # Create plain text content with unsubscribe link
    text_content = '''Welcome to Daily Meme Digest! 🎉

Hey there, meme lover!

Thanks for subscribing to Daily Meme Digest! We're excited to have you on board.

What's coming soon:
- 🎭 Fresh memes delivered daily
- 📱 Mobile-friendly newsletter
- 🎯 Curated content just for you
- 🚀 Early access to new features

We're currently setting up our meme pipeline to bring you the best content every day. Stay tuned for the first batch of memes coming soon!

In the meantime, you can:
- 📧 Check your email preferences
- 🌐 Visit our website for updates
- 📱 Follow us on social media

Thanks for being part of our meme community!

Best regards,
The Daily Meme Digest Team

---
You're receiving this because you subscribed to Daily Meme Digest.
Visit our website: https://dailymemedigest.com
Unsubscribe: {$unsubscribe}'''
    
    subject = "Welcome to Daily Meme Digest! 🎉"
    
    debug_print("✅ Created welcome newsletter content")
    
    return {
        'subject': subject,
        'html_content': html_content,
        'text_content': text_content
    }

def create_campaign(content):
    """Create a new Brevo campaign with the correct structure"""
    debug_print("📧 Creating Brevo campaign...")
    
    api_key = os.getenv('BREVO_API_KEY')
    list_id = os.getenv('BREVO_LIST_ID')
    from_email = os.getenv('BREVO_FROM_EMAIL')
    from_name = os.getenv('BREVO_FROM_NAME', 'Daily Meme Digest')
    
    if not all([api_key, list_id, from_email]):
        debug_print("❌ Missing required Brevo configuration")
        return None
    
    headers = {
        'api-key': api_key,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Create the campaign data for Brevo
    campaign_data = {
        'name': f'Daily Meme Digest - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
        'subject': content['subject'],
        'sender': {
            'name': from_name,
            'email': from_email
        },
        'htmlContent': content['html_content'],
        'textContent': content['text_content'],
        'recipients': {
            'listIds': [int(list_id)]
        },
        'type': 'classic'
    }
    
    try:
        response = requests.post(
            'https://api.brevo.com/v3/emailCampaigns',
            headers=headers,
            json=campaign_data,
            timeout=10
        )
        
        debug_print(f"📡 Campaign creation response: {response.status_code}")
        
        if response.status_code in [200, 201]:
            campaign_info = response.json()
            campaign_id = campaign_info.get('id')
            debug_print(f"✅ Campaign created with ID: {campaign_id}")
            return campaign_id
        else:
            debug_print(f"❌ Campaign creation failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        debug_print(f"❌ Error creating campaign: {str(e)}")
        return None

def send_campaign(campaign_id):
    """Send the campaign using the send endpoint"""
    debug_print(f"📤 Sending campaign {campaign_id}...")
    
    api_key = os.getenv('BREVO_API_KEY')
    
    headers = {
        'api-key': api_key,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.post(
            f'https://api.brevo.com/v3/emailCampaigns/{campaign_id}/sendNow',
            headers=headers,
            timeout=10
        )
        
        debug_print(f"📡 Send response: {response.status_code}")
        
        if response.status_code == 204:  # Brevo returns 204 for successful send
            debug_print("✅ Campaign sent successfully!")
            return True
        else:
            debug_print(f"❌ Send failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        debug_print(f"❌ Error sending campaign: {str(e)}")
        return False

def main():
    """Main function to send the newsletter"""
    debug_print("🚀 Starting DailyMemeDigest newsletter sender...")
    debug_print("=" * 60)
    
    # Step 1: Environment Check
    debug_print("📋 Checking environment variables...")
    required_vars = ['BREVO_API_KEY', 'BREVO_LIST_ID', 'BREVO_FROM_EMAIL']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        debug_print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        debug_print("Please set these variables in your environment or .env file")
        debug_print("Note: BREVO_FROM_NAME is optional (defaults to 'Daily Meme Digest')")
        return
    
    debug_print("✅ All required environment variables are set")
    
    # Step 2: Test Brevo Connection
    if not test_brevo_connection():
        debug_print("❌ Brevo connection failed. Exiting.")
        return
    
    # Step 3: Get List Information
    list_info = get_list_info()
    if not list_info:
        debug_print("❌ Failed to get list information. Exiting.")
        return
    
    # Step 4: Create Newsletter Content
    debug_print("📧 Creating welcome newsletter...")
    content = create_newsletter_content([])  # Empty list since we're not using memes yet
    
    # Debug: Show the from email being used
    from_email = os.getenv('BREVO_FROM_EMAIL')
    debug_print(f"📧 Using from email: {from_email}")
    
    # Step 5: Create and Send Campaign
    campaign_id = create_campaign(content)
    if not campaign_id:
        debug_print("❌ Failed to create campaign. Exiting.")
        return
    
    # Step 6: Send Campaign
    if send_campaign(campaign_id):
        debug_print("🎉 Newsletter sent successfully!")
        debug_print("=" * 60)
        debug_print("✅ Process completed successfully!")
    else:
        debug_print("❌ Failed to send newsletter")
        debug_print("Campaign was created but not sent. You may need to send it manually.")

if __name__ == "__main__":
    main()