#!/usr/bin/env python3
"""
Simple run script for the Flask WatchTower application.
This script loads environment variables and starts the Flask development server.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import and run the Flask app
from app import app

if __name__ == '__main__':
    # Check if Gemini API key is set
    if not os.getenv('GEMINI_API_KEY'):
        print("⚠️  Warning: GEMINI_API_KEY not found in environment variables.")
        print("   Please create a .env file with your Gemini API key.")
        print("   Example: GEMINI_API_KEY=your_api_key_here")
        print()
    
    print("🛡️  Starting WatchTower AI Security Camera Analyst...")
    print("📍 Server will be available at: http://localhost:5000")
    print("🔧 Running in development mode with auto-reload enabled")
    print()
    
    app.run(
        debug=True, 
        host='0.0.0.0', 
        port=5000,
        threaded=True
    )