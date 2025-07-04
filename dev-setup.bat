@echo off
echo ========================================
echo AI Meme Newsletter - Development Setup
echo ========================================

echo.
echo This script will help you set up the development environment
echo for the Flask + React structure.
echo.

echo Step 1: Moving package-lock.json to frontend/
if exist package-lock.json (
    move package-lock.json frontend\
    echo ✓ Moved package-lock.json to frontend/
) else (
    echo - package-lock.json not found in root
)

echo.
echo Step 2: Moving build directory to frontend/
if exist build (
    move build frontend\
    echo ✓ Moved build directory to frontend/
) else (
    echo - build directory not found in root
)

echo.
echo Step 3: Checking frontend dependencies...
cd frontend
if exist node_modules (
    echo ✓ Frontend dependencies already installed
) else (
    echo Installing frontend dependencies...
    npm install
)

echo.
echo Step 4: Building React app...
npm run build
if %errorlevel% equ 0 (
    echo ✓ React app built successfully
) else (
    echo ✗ Failed to build React app
    exit /b 1
)

cd ..

echo.
echo Step 5: Checking backend dependencies...
cd backend
if exist venv (
    echo ✓ Python virtual environment exists
) else (
    echo Creating Python virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing backend dependencies...
pip install -r requirements.txt

cd ..

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To run the application:
echo.
echo 1. Start the Flask backend:
echo    cd backend
echo    python app.py
echo.
echo 2. For development, you can also run React separately:
echo    cd frontend
echo    npm start
echo.
echo The Flask server will serve the built React app at:
echo http://localhost:5001
echo. 