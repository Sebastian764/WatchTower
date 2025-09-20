# 🛡️ WatchTower - AI Security Camera Analyst

A simple Flask web application that uses Google's Gemini AI to analyze security camera footage and automatically detect incidents like robberies, fights, medical emergencies, and vandalism.

## Features

- **Video Upload**: Simple drag-and-drop interface for MP4 video files
- **AI Analysis**: Powered by Google Gemini 2.0 Flash for accurate incident detection
- **Incident Classification**: Automatically categorizes incidents (Robbery, Medical Emergency, Altercation/Fight, Vandalism, Other)
- **Timestamp Detection**: Identifies when incidents occur in the video
- **Action Recommendations**: Suggests appropriate responses (Notify Authorities, Notify Paramedics, Continue Monitoring)

## Quick Start

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your Gemini API key:**
   ```bash
   cp .env.example .env
   # Edit .env and add your Gemini API key
   ```

3. **Run the application:**
   ```bash
   python run.py
   ```

4. **Open your browser to:** `http://localhost:5000`

## Getting a Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file as `GEMINI_API_KEY=your_key_here`

## File Structure

```
WatchTower/
├── app.py              # Main Flask application
├── run.py              # Development server startup script
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
├── templates/
│   └── index.html     # Web interface
└── uploads/           # Temporary video storage (auto-created)
```

## Usage

1. Upload an MP4 video file (max 100MB)
2. Click "Analyze Video" 
3. Wait for AI analysis to complete
4. Review detected incidents with timestamps and recommended actions

## Technology Stack

- **Backend**: Python Flask
- **AI**: Google Gemini 2.0 Flash
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **File Handling**: Werkzeug

## Development

The application runs in development mode with auto-reload enabled. Uploaded videos are temporarily stored in the `uploads/` directory and automatically deleted after analysis.

## Security Note

This application is designed for development and demonstration purposes. For production use, consider implementing additional security measures like user authentication, rate limiting, and secure file handling.
