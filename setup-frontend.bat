@echo off

REM Setup script for React frontend (Windows)

echo 🚀 Setting up AI Meme Newsletter React Frontend...

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js first.
    echo    Download from: https://nodejs.org/
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ npm is not installed. Please install npm first.
    pause
    exit /b 1
)

echo 📦 Installing React dependencies...
npm install

if %errorlevel% equ 0 (
    echo ✅ Dependencies installed successfully!
) else (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo 🔨 Building React app...
npm run build

if %errorlevel% equ 0 (
    echo ✅ React app built successfully!
    echo 🎉 Frontend setup complete!
    echo.
    echo Next steps:
    echo 1. Copy env.example to .env and configure your API keys
    echo 2. Run: python app.py
    echo 3. Open http://localhost:5001 in your browser
) else (
    echo ❌ Failed to build React app
    pause
    exit /b 1
)

pause 