# 🎭 AI Meme Factory

> Turn the latest AI news into viral memes using GPT-powered humor!

**Built for Sundai Club Hackathon** - designed to reach 1K users or $1K revenue in one week.

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone <your-repo>
cd ai-meme-factory
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Get API Keys
- **OpenAI**: https://platform.openai.com/api-keys
- **News API**: https://newsapi.org/ (free - 100 requests/day)

### 3. Configure Environment
```bash
# Copy and edit .env file
cp .env.example .env
# Add your API keys to .env
```

### 4. Run the App
```bash
python app.py
# Visit: http://localhost:5000
```

## 📁 Project Structure

```
ai-meme-factory/
├── app.py                    # Main Flask application
├── src/                      # Source code modules
│   ├── config.py            # Configuration settings
│   ├── models.py            # Data models
│   ├── database.py          # Database operations
│   ├── news_aggregator.py   # News fetching
│   ├── meme_generator.py    # AI meme generation
│   └── utils.py             # Utility functions
├── templates/               # HTML templates
│   ├── base.html           # Base template
│   ├── index.html          # Main page
│   └── components/         # Reusable components
├── static/                 # Static assets
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript
│   └── images/            # Images
├── tests/                 # Test files
└── scripts/               # Utility scripts
```

## ✨ Features

- 🤖 **Full AI Pipeline**: GPT text generation + gpt-image-1 image creation
- 📰 **Live News Integration**: Real AI news from major tech publications
- 🎭 **6 Meme Templates**: Drake, Expanding Brain, Distracted Boyfriend, etc.
- 🗳️ **Community Voting**: Upvote the best memes
- 📱 **Mobile Responsive**: Works on all devices
- 🚀 **Production Ready**: Deployed on Heroku

## 🛠️ Tech Stack

- **Backend**: Python Flask
- **AI**: OpenAI gpt-image-1 + GPT-3.5-turbo
- **News**: NewsAPI.org
- **Database**: SQLite
- **Frontend**: HTML/CSS/JS
- **Deployment**: Heroku

## 💰 Business Model

1. **Premium Templates** ($2.99/month)
2. **API Access** ($0.10/meme)
3. **Sponsored Memes** ($50-200/meme)
4. **Pro Analytics** ($9.99/month)

## 🎯 Demo Script

**Opening**: "What if AI could create memes about AI?"
**Demo**: Live generation from real news
**Business**: Clear monetization + viral potential
**Technical**: Production-ready, scalable architecture

## 🚀 Deployment

```bash
# Heroku
heroku create ai-meme-factory
heroku# ==============================================================================
# PROJECT STRUCTURE
# ==============================================================================

ai-meme-factory/
│
├── 📁 Root Configuration
│   ├── app.py                      # Main Flask application
│   ├── requirements.txt            # Python dependencies
│   ├── .env                        # Environment variables
│   ├── .gitignore                 # Git ignore rules
│   ├── README.md                  # Project documentation
│   ├── Procfile                   # Heroku deployment
│   ├── app.json                   # Heroku one-click deploy
│   └── run.sh                     # Development startup script
│
├── 📁 src/                        # Source code modules
│   ├── __init__.py                # Package initialization
│   ├── config.py                  # Configuration settings
│   ├── models.py                  # Data models
│   ├── database.py                # Database operations
│   ├── news_aggregator.py         # News fetching logic
│   ├── meme_generator.py          # AI meme generation
│   └── utils.py                   # Utility functions
│
├── 📁 templates/                  # HTML templates
│   ├── base.html                  # Base template
│   ├── index.html                 # Main page
│   └── components/                # Reusable components
│       ├── header.html            # Header component
│       ├── news_ticker.html       # News display
│       └── meme_card.html         # Meme display card
│
├── 📁 static/                     # Static assets
│   ├── 📁 css/
│   │   ├── main.css               # Main styles
│   │   └── components.css         # Component styles
│   ├── 📁 js/
│   │   ├── main.js                # Main JavaScript
│   │   ├── meme_generator.js      # Meme generation logic
│   │   └── news_display.js        # News display logic
│   └── 📁 images/
│       ├── logo.png               # App logo
│       └── favicon.ico            # Favicon
│
├── 📁 tests/                      # Test files
│   ├── __init__.py
│   ├── test_app.py                # App tests
│   ├── test_meme_generator.py     # Meme generation tests
│   ├── test_news_aggregator.py    # News aggregation tests
│   └── test_database.py           # Database tests
│
├── 📁 scripts/                    # Utility scripts
│   ├── setup_project.py           # Automated setup
│   ├── test_apis.py               # API testing
│   └── deploy.py                  # Deployment script
│
└── 📁 docs/                       # Documentation
    ├── API.md                     # API documentation
    ├── DEPLOYMENT.md              # Deployment guide
    └── DEMO.md                    # Demo script