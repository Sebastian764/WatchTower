from flask import Flask, request, render_template, jsonify
import os
import json
import google.generativeai as genai
from werkzeug.utils import secure_filename
from enum import Enum

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configure Gemini API
gemini_api_key = os.getenv('GEMINI_API_KEY')
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)

class IncidentType(Enum):
    NONE = 'None'
    ROBBERY = 'Robbery'
    MEDICAL_EMERGENCY = 'Medical Emergency'
    FIGHT = 'Altercation/Fight'
    VANDALISM = 'Vandalism'
    OTHER = 'Other'

class RecommendedAction(Enum):
    NONE = 'None'
    NOTIFY_AUTHORITIES = 'Notify Authorities'
    NOTIFY_PARAMEDICS = 'Notify Paramedics'
    MONITOR = 'Continue Monitoring'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_video():
    if not gemini_api_key:
        return jsonify({'error': 'Gemini API key not configured'}), 500
    
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Upload to Gemini
        print(f"Uploading {filename} to Gemini...")
        video_file = genai.upload_file(filepath)
        
        # Wait for the file to be processed
        print("Waiting for file to be processed...")
        import time
        while video_file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(2)
            video_file = genai.get_file(video_file.name)
        
        if video_file.state.name == "FAILED":
            raise Exception("File processing failed")
        
        print(f"\nFile {video_file.name} is ready for analysis")
        
        # Create the model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = """You are an expert security AI system. Analyze this video footage carefully. 
        Identify any security incidents like robberies, medical emergencies, fights, vandalism, or other suspicious activities. 
        For each incident, provide its timestamp, a description (LIMITED TO 90 CHARACTERS OR LESS), classify its type, and recommend an action. 
        If there are no incidents, return an empty 'incidents' array. 
        Respond ONLY with a JSON object with this structure:
        {
            "incidents": [
                {
                    "timestamp": "00:45",
                    "incidentType": "Robbery|Medical Emergency|Altercation/Fight|Vandalism|Other|None",
                    "description": "Brief but detailed description of what you observed (MAX 140 CHARACTERS)",
                    "recommendedAction": "Notify Authorities|Notify Paramedics|Continue Monitoring|None"
                }
            ]
        }"""
        
        # Generate content
        print("Generating AI analysis...")
        response = model.generate_content([prompt, video_file])
        
        # Clean up files
        try:
            genai.delete_file(video_file.name)
            print(f"Deleted Gemini file: {video_file.name}")
        except Exception as cleanup_error:
            print(f"Warning: Could not delete Gemini file: {cleanup_error}")
        
        os.remove(filepath)
        print(f"Deleted local file: {filepath}")
        
        # Parse response
        response_text = response.text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:-3]
        elif response_text.startswith('```'):
            response_text = response_text[3:-3]
            
        result = json.loads(response_text)
        # If incidents array is not empty, send SMS notification for each incident
        incidents = result.get('incidents', [])
        if incidents:
            import subprocess
            for incident in incidents:
                incident_type = incident.get('incidentType', 'Unknown')
                description = incident.get('description', '')
                sms_message = f"Incident detected: {incident_type} - {description}"
                # Call sms_notify.py to send SMS
                try:
                    subprocess.run([
                        'python3', 'sms_notify.py', '--notify', 'true', '--message', sms_message
                    ], check=True)
                except Exception as sms_err:
                    print(f"Failed to send SMS notification: {sms_err}")
        return jsonify(result)
        
    except Exception as e:
        # Clean up local file if it exists
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
            
        # Clean up Gemini file if it exists
        if 'video_file' in locals():
            try:
                genai.delete_file(video_file.name)
            except:
                pass  # File might not exist or already deleted
                
        print(f"Error during analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)