#!/bin/bash

# Setup script for React frontend

echo "🚀 Setting up AI Meme Newsletter React Frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    echo "   Download from: https://nodejs.org/"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "📦 Installing React dependencies..."
npm install

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "🔨 Building React app..."
npm run build

if [ $? -eq 0 ]; then
    echo "✅ React app built successfully!"
    echo "🎉 Frontend setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Copy env.example to .env and configure your API keys"
    echo "2. Run: python app.py"
    echo "3. Open http://localhost:5001 in your browser"
else
    echo "❌ Failed to build React app"
    exit 1
fi 