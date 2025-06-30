#!/usr/bin/env python
"""
Unified launcher for AI Meme Factory
Works on all operating systems with Python

Usage:
    python meme.py              # Run with defaults
    python meme.py local        # Run in local mode
    python meme.py --port 8080  # Run with custom port
    python meme.py dev-local    # Run with preset configuration
"""

import sys
import subprocess
import json
import os

# Default configuration
DEFAULT_CONFIG = {
    "mode": "cloud",
    "port": 5001
}

def load_config():
    """Load configuration from meme.config.json if it exists"""
    try:
        with open('meme.config.json', 'r') as f:
            return json.load(f)
    except:
        return None

def print_usage():
    """Print usage information"""
    print("AI Meme Factory Launcher\n")
    print("Usage:")
    print("  python meme.py              # Run with defaults (cloud mode)")
    print("  python meme.py local        # Run in local mode")
    print("  python meme.py cloud        # Run in cloud mode")
    print("  python meme.py --port 8080  # Specify port")
    print("  python meme.py local 8080   # Local mode with port")
    
    config = load_config()
    if config and 'shortcuts' in config:
        print("\nShortcuts:")
        for name, settings in config['shortcuts'].items():
            mode = settings.get('mode', 'cloud')
            port = settings.get('port', 5001)
            print(f"  python meme.py {name:<12} # {mode} mode on port {port}")
    
    print("\nRequired API Keys:")
    print("  Both modes: NEWS_API_KEY (FREE), GEMINI_API_KEY (FREE)")
    print("  Cloud mode: OPENAI_API_KEY (PAID)")
    print("\nGet API keys:")
    print("  News API: https://newsapi.org/")
    print("  Gemini API: https://aistudio.google.com/apikey")
    print("  OpenAI API: https://platform.openai.com/settings/organization/api-keys")

def run_app(mode='cloud', port=5001):
    """Run the application"""
    cmd = [sys.executable, 'app.py']
    
    if mode == 'local':
        cmd.append('--local')
    
    if port != 5001:
        cmd.extend(['--port', str(port)])
    
    print(f"Starting in {mode.upper()} mode on port {port}...")
    print(f"Command: {' '.join(cmd)}\n")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def main():
    """Main entry point"""
    args = sys.argv[1:]
    config = load_config()
    
    # No arguments - use defaults
    if not args:
        mode = DEFAULT_CONFIG['mode']
        port = DEFAULT_CONFIG['port']
        if config:
            mode = config.get('default_mode', mode)
            port = config.get('default_port', port)
        run_app(mode, port)
        return
    
    # Help
    if args[0] in ['-h', '--help', 'help']:
        print_usage()
        return
    
    # Check for shortcuts
    if config and 'shortcuts' in config and args[0] in config['shortcuts']:
        shortcut = config['shortcuts'][args[0]]
        run_app(
            mode=shortcut.get('mode', 'cloud'),
            port=shortcut.get('port', 5001)
        )
        return
    
    # Parse arguments
    mode = 'cloud'
    port = 5001
    
    for i, arg in enumerate(args):
        if arg in ['local', 'cloud']:
            mode = arg
        elif arg == '--port' and i + 1 < len(args):
            try:
                port = int(args[i + 1])
            except ValueError:
                print(f"Error: Invalid port: {args[i + 1]}")
                sys.exit(1)
        elif arg.isdigit():
            port = int(arg)
    
    run_app(mode, port)

if __name__ == "__main__":
    main()