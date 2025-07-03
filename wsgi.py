"""
WSGI entry point for Cloud Run
Bypasses argparse and runs in cloud mode
"""

import os
import sys

# Force cloud mode for production
os.environ['MEME_MODE'] = 'cloud'

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import after setting up environment
from app import create_app

# Create application instance
application = create_app()

# For gunicorn
app = application

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)