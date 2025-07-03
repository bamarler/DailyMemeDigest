# AI Meme Newsletter

A modern React-based newsletter subscription system for AI enthusiasts, featuring a beautiful 4-page flow for email signup and preference selection.

## 🚀 Features

- **Modern React Frontend**: Built with React 18, Tailwind CSS, and React Router
- **4-Page User Flow**: 
  1. Email signup with validation
  2. News preference selection with toggle switches
  3. Confirmation email sent notification
  4. Thank you page with auto-redirect
- **Mailchimp Integration**: Seamless email list management and preference tracking
- **Responsive Design**: Beautiful UI that works on all devices
- **API-First Backend**: Flask backend with RESTful API endpoints

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

### 2. Setup Python Backend
```bash
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

### 3. Setup React Frontend

**Option A: Using the setup script (Recommended)**
```bash
# On Windows:
setup-frontend.bat

# On macOS/Linux:
chmod +x setup-frontend.sh
./setup-frontend.sh
```

**Option B: Manual setup**
```bash
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

### Development Mode
```bash
# Start the Flask backend
python app.py

# In a separate terminal, start React development server
npm start
```

### Production Mode
```bash
# Build the React app
npm run build

# Start the Flask backend (serves the built React app)
python app.py
```

The application will be available at `http://localhost:5001`

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

## 🎨 Customization

### Styling
The app uses Tailwind CSS for styling. You can customize the design by:
- Modifying `tailwind.config.js` for theme changes
- Updating component classes in the React components
- Adding custom CSS in `src/index.css`

### News Categories
Edit the categories in `src/pages/NewsPreferences.js`:
```javascript
const categories = [
  { key: 'openai', label: 'OpenAI & ChatGPT', description: '...' },
  // Add or modify categories here
];
```

### Mailchimp Integration
The Mailchimp integration is handled in `src/mailchimp_service.py`. You can:
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
   - Clear node_modules and reinstall: `rm -rf node_modules && npm install`
   - Check for version conflicts in package.json

4. **Flask backend errors**
   - Ensure all Python dependencies are installed
   - Check that your virtual environment is activated

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
