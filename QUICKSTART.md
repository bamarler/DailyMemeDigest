# Quick Start Guide

Get the AI Meme Newsletter up and running in 5 minutes!

## 🚀 Quick Setup

### 1. Prerequisites Check
Make sure you have:
- ✅ Node.js installed (`node --version`)
- ✅ Python 3.8+ installed (`python --version`)
- ✅ Git installed

### 2. Clone and Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd AIMemeNewletter

# Setup Python backend
python -m venv venv
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # macOS/Linux

pip install -r requirements.txt

# Setup React frontend (Windows)
setup-frontend.bat

# OR for macOS/Linux:
chmod +x setup-frontend.sh
./setup-frontend.sh
```

### 3. Configure Environment
```bash
# Copy environment template
cp env.example .env

# Edit .env with your keys (at minimum, add a dummy MAILCHIMP_API_KEY)
```

**Minimum required for testing:**
```env
MAILCHIMP_API_KEY=test-key
MAILCHIMP_SERVER_PREFIX=us1
MAILCHIMP_LIST_ID=test-list
```

### 4. Run the Application
```bash
python app.py
```

Open http://localhost:5001 in your browser!

## 🎯 What You'll See

1. **Page 1**: Email signup form
2. **Page 2**: News preference toggles
3. **Page 3**: Confirmation message
4. **Page 4**: Thank you with auto-redirect

## 🔧 Production Setup

For production, you'll need real API keys:

1. **Mailchimp Setup**:
   - Sign up at https://mailchimp.com/
   - Get your API key from Account → Extras → API Keys
   - Find your server prefix (e.g., 'us1') in the API key URL
   - Create an audience and get the List ID

2. **Update .env**:
```env
MAILCHIMP_API_KEY=your-real-api-key
MAILCHIMP_SERVER_PREFIX=us1
MAILCHIMP_LIST_ID=your-list-id
```

## 🐛 Common Issues

**"Node.js not found"**
- Download from https://nodejs.org/

**"npm not found"**
- Node.js includes npm, reinstall Node.js

**Build fails**
- Try: `rm -rf node_modules && npm install`

**Flask errors**
- Ensure virtual environment is activated
- Check all dependencies are installed

## 📞 Need Help?

- Check the full [README.md](README.md) for detailed instructions
- Open an issue in the repository
- Check the troubleshooting section in the main README 