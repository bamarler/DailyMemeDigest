# AI Meme Newsletter

A modern Flask + React newsletter subscription system for AI enthusiasts, featuring a beautiful 4-page flow for email signup and preference selection.

## 🚀 Features

- **Modern React Frontend**: Built with React 18, Tailwind CSS, and React Router
- **Flask Backend**: RESTful API with Mailchimp integration
- **4-Page User Flow**: 
  1. Email signup with validation
  2. News preference selection with toggle switches
  3. Confirmation email sent notification
  4. Thank you page with auto-redirect
- **Mailchimp Integration**: Seamless email list management and preference tracking
- **Responsive Design**: Beautiful UI that works on all devices
- **Production Ready**: Flask serves the built React app

## 📁 Project Structure

```
AIMemeNewletter/
├── frontend/           # React application
│   ├── src/           # React source code
│   ├── public/        # Static assets
│   ├── build/         # Built React app (served by Flask)
│   ├── package.json   # Node.js dependencies
│   └── tailwind.config.js
├── backend/           # Flask application
│   ├── src/           # Python source code
│   ├── templates/     # Jinja templates (legacy)
│   ├── app.py         # Main Flask application
│   └── requirements.txt
├── dev-setup.bat      # Windows setup script
├── dev-setup.sh       # Linux/Mac setup script
└── README.md
```

## 📋 Prerequisites

- **Node.js** (v16 or higher) - [Download here](https://nodejs.org/)
- **Python** (v3.8 or higher)
- **Mailchimp Account** - [Sign up here](https://mailchimp.com/)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd AIMemeNewletter
```

### 2. Quick Setup (Recommended)
```bash
# On Windows:
dev-setup.bat

# On macOS/Linux:
chmod +x dev-setup.sh
./dev-setup.sh
```

### 3. Manual Setup

**Backend Setup:**
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

**Frontend Setup:**
```bash
cd frontend

# Install React dependencies
npm install

# Build the React app
npm run build
```

### 4. Configure Environment Variables
```bash
# Copy the example environment file
cp env.example .env

# Edit .env with your API keys
```

Required environment variables:
- `MAILCHIMP_API_KEY`: Your Mailchimp API key
- `MAILCHIMP_SERVER_PREFIX`: Your Mailchimp server prefix (e.g., 'us1')
- `MAILCHIMP_LIST_ID`: Your Mailchimp audience/list ID
- `NEWS_API_KEY`: Your NewsAPI.org API key (optional, for news aggregation)
- `OPENAI_API_KEY`: Your OpenAI API key (optional, for meme generation)

## 🚀 Running the Application

### Production Mode (Recommended)
```bash
# Start the Flask backend (serves the built React app)
cd backend
python app.py
```

The application will be available at `http://localhost:5001`

### Development Mode
```bash
# Terminal 1: Start Flask backend
cd backend
python app.py

# Terminal 2: Start React development server
cd frontend
npm start
```

React dev server will run on `http://localhost:3000` with API proxy to Flask.

## 📱 User Flow

### Page 1: Email Signup
- Clean, modern design with email validation
- Real-time email format checking
- Integration with Mailchimp for list management

### Page 2: News Preferences
- 10 AI news categories with toggle switches
- Categories include: OpenAI, Claude, Machine Learning, Generative AI, etc.
- Preferences are saved to Mailchimp merge fields

### Page 3: Confirmation Sent
- Clear instructions for email confirmation
- Spam folder guidance
- Professional confirmation message

### Page 4: Thank You
- Success confirmation
- 5-second auto-redirect to home page
- Clean, satisfying completion experience

## 🔧 API Endpoints

- `POST /api/subscribe` - Subscribe email to Mailchimp list
- `POST /api/preferences` - Update user preferences
- `GET /api/confirm/<token>` - Confirm email subscription
- `POST /api/generate` - Generate memes (legacy feature)
- `GET /api/memes` - Get meme history (legacy feature)
- `GET /api/news` - Get news articles (legacy feature)

## 🎨 Customization

### Frontend Styling
The React app uses Tailwind CSS for styling. You can customize the design by:
- Modifying `frontend/tailwind.config.js` for theme changes
- Updating component classes in the React components
- Adding custom CSS in `frontend/src/index.css`

### News Categories
Edit the categories in `frontend/src/pages/NewsPreferences.js`:
```javascript
const categories = [
  { key: 'openai', label: 'OpenAI & ChatGPT', description: '...' },
  // Add or modify categories here
];
```

### Backend Configuration
The Flask backend configuration is in `backend/app.py`. You can:
- Modify API endpoints
- Add new routes
- Customize error handling

### Mailchimp Integration
The Mailchimp integration is handled in `backend/src/mailchimp_service.py`. You can:
- Customize merge field names
- Add additional subscriber data
- Implement custom email templates

## 🐛 Troubleshooting

### Common Issues

1. **Node.js not found**
   - Install Node.js from https://nodejs.org/
   - Ensure it's added to your PATH

2. **Mailchimp API errors**
   - Verify your API key, server prefix, and list ID
   - Check that your Mailchimp account is active

3. **Build errors**
   - Clear node_modules and reinstall: `cd frontend && rm -rf node_modules && npm install`
   - Check for version conflicts in package.json

4. **Flask backend errors**
   - Ensure all Python dependencies are installed
   - Check that your virtual environment is activated
   - Verify the React build exists in `frontend/build/`

5. **404 errors on React routes**
   - Ensure the React app is built: `cd frontend && npm run build`
   - Check that `frontend/build/index.html` exists

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For support, please open an issue in the GitHub repository or contact the development team.
