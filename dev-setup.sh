#!/bin/bash

echo "========================================"
echo "AI Meme Newsletter - Development Setup"
echo "========================================"

echo
echo "This script will help you set up the development environment"
echo "for the Flask + React structure."
echo

echo "Step 1: Moving package-lock.json to frontend/"
if [ -f "package-lock.json" ]; then
    mv package-lock.json frontend/
    echo "✓ Moved package-lock.json to frontend/"
else
    echo "- package-lock.json not found in root"
fi

echo
echo "Step 2: Moving build directory to frontend/"
if [ -d "build" ]; then
    mv build frontend/
    echo "✓ Moved build directory to frontend/"
else
    echo "- build directory not found in root"
fi

echo
echo "Step 3: Checking frontend dependencies..."
cd frontend
if [ -d "node_modules" ]; then
    echo "✓ Frontend dependencies already installed"
else
    echo "Installing frontend dependencies..."
    npm install
fi

echo
echo "Step 4: Building React app..."
npm run build
if [ $? -eq 0 ]; then
    echo "✓ React app built successfully"
else
    echo "✗ Failed to build React app"
    exit 1
fi

cd ..

echo
echo "Step 5: Checking backend dependencies..."
cd backend
if [ -d "venv" ]; then
    echo "✓ Python virtual environment exists"
else
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing backend dependencies..."
pip install -r requirements.txt

cd ..

echo
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo
echo "To run the application:"
echo
echo "1. Start the Flask backend:"
echo "   cd backend"
echo "   python app.py"
echo
echo "2. For development, you can also run React separately:"
echo "   cd frontend"
echo "   npm start"
echo
echo "The Flask server will serve the built React app at:"
echo "http://localhost:5001"
echo 