#!/usr/bin/env python3
"""
Setup script for React frontend
Replaces setup-frontend.bat and setup-frontend.sh
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to {description.lower()}")
        print(f"Error: {e.stderr}")
        return False

def check_node_installed():
    """Check if Node.js is installed"""
    try:
        subprocess.run(["node", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_npm_installed():
    """Check if npm is installed"""
    try:
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up AI Meme Newsletter React Frontend...")
    
    # Check if Node.js is installed
    if not check_node_installed():
        print("❌ Node.js is not installed. Please install Node.js first.")
        print("   Download from: https://nodejs.org/")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Check if npm is installed
    if not check_npm_installed():
        print("❌ npm is not installed. Please install npm first.")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Change to frontend directory
    frontend_dir = Path(__file__).parent
    os.chdir(frontend_dir)
    
    # Install dependencies
    if not run_command("npm install", "Installing React dependencies"):
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Build React app
    if not run_command("npm run build", "Building React app"):
        input("Press Enter to exit...")
        sys.exit(1)
    
    print("🎉 Frontend setup complete!")
    print()
    print("Next steps:")
    print("1. Copy env.example to .env and configure your API keys")
    print("2. Run: python app.py")
    print("3. Open http://localhost:5001 in your browser")
    
    if platform.system() == "Windows":
        input("Press Enter to exit...")

if __name__ == "__main__":
    main() 