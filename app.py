import os
import cv2
import numpy as np
import base64
import json
import threading
from flask import Flask, request, jsonify, render_template, url_for, send_from_directory
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from video_processor import process_video, analyze_full_video
from yolo_detector import YOLODetection

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 MB max file size

# Initialize YOLO Detector
print("Initializing YOLO Detector...")
yolo = YOLODetection()
print("YOLO Detector initialized.")

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Store analysis results in memory (in production, use Redis or database)
analysis_cache = {}

def allowed_file(filename):
    """Checks if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Renders the main HTML page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handles video upload and calls the main processing function (legacy endpoint)."""
    if 'video' not in request.files:
        return jsonify({'error': 'No video part in the request'}), 400
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No video selected for uploading'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(video_path)
        
        results = process_video(video_path)
        video_url = url_for('uploaded_file', filename=filename)

        return jsonify({'results': results, 'video_path': video_url})
    else:
        return jsonify({'error': 'Invalid file type'}), 400

@app.route('/analyze_full', methods=['POST'])
def analyze_full():
    """Analyzes the full video without splitting and returns timestamps of incidents."""
    print("Received request to /analyze_full")
    
    try:
        if 'video' not in request.files:
            print("Error: No video file in request")
            return jsonify({'error': 'No video part in the request'}), 400
        
        file = request.files['video']
        if file.filename == '':
            print("Error: Empty filename")
            return jsonify({'error': 'No video selected'}), 400
        
        print(f"Processing file: {file.filename}")
        
        if file and allowed_file(file.filename):
            # Generate unique filename to avoid conflicts
            import uuid
            unique_id = str(uuid.uuid4())[:8]
            original_filename = secure_filename(file.filename)
            filename = f"{unique_id}_{original_filename}"
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            print(f"Saving file to: {video_path}")
            file.save(video_path)
            
            # Check if file was saved successfully
            if not os.path.exists(video_path):
                print(f"Error: File not saved at {video_path}")
                return jsonify({'error': 'Failed to save video file'}), 500
            
            print(f"File saved successfully. Size: {os.path.getsize(video_path)} bytes")
            
            # Check if we have cached results
            if filename in analysis_cache:
                print(f"Returning cached results for {filename}")
                return jsonify({'alerts': analysis_cache[filename]})
            
            # Analyze the full video
            try:
                print(f"Starting analysis of {video_path}")
                alerts = analyze_full_video(video_path)
                print(f"Analysis complete. Found {len(alerts)} alerts")
                
                # Cache the results
                analysis_cache[filename] = alerts
                
                # Optional: Clean up the file after analysis
                # Commented out so you can review the uploaded files
                # try:
                #     os.remove(video_path)
                #     print(f"Cleaned up file: {video_path}")
                # except Exception as e:
                #     print(f"Warning: Could not remove file {video_path}: {e}")
                
                return jsonify({'alerts': alerts})
                
            except Exception as e:
                print(f"Error during video analysis: {str(e)}")
                import traceback
                traceback.print_exc()
                
                # Try to clean up the file if analysis failed
                try:
                    if os.path.exists(video_path):
                        os.remove(video_path)
                except:
                    pass
                
                return jsonify({'error': f'Failed to analyze video: {str(e)}'}), 500
        else:
            print(f"Error: Invalid file type for {file.filename}")
            return jsonify({'error': 'Invalid file type. Allowed types: ' + ', '.join(ALLOWED_EXTENSIONS)}), 400
            
    except Exception as e:
        print(f"Unexpected error in /analyze_full: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/process_frame', methods=['POST'])
def handle_frame_processing():
    """Receives a frame from the frontend and returns YOLO detections."""
    data = request.get_json()
    if not data or 'image_data' not in data:
        return jsonify({'error': 'No image data provided'}), 400
    
    try:
        # Decode the image data sent from the browser
        img_data = data['image_data'].split(',')[1]
        decoded_data = base64.b64decode(img_data)
        np_arr = np.frombuffer(decoded_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({'error': 'Could not decode image'}), 400

        # Use the detect_humans method from your class instance
        boxes = yolo.detect_humans(frame)
        
        # Convert the results to the format the frontend expects
        detections = [{'x': box[0], 'y': box[1], 'w': box[2], 'h': box[3]} for box in boxes]
        
        return jsonify({'detections': detections})

    except Exception as e:
        print(f"Error processing frame: {e}")
        return jsonify({'error': 'Server error during frame processing'}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serves the uploaded video file to the browser."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/get_analysis/<filename>')
def get_analysis(filename):
    """Returns cached analysis for a video file."""
    if filename in analysis_cache:
        return jsonify({'alerts': analysis_cache[filename]})
    return jsonify({'alerts': []})

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint to verify server is running."""
    return jsonify({'status': 'OK', 'message': 'Server is running'}), 200

if __name__ == '__main__':
    print("\n" + "="*50)
    print("CCTV Monitoring System Starting...")
    print("="*50)
    print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"Allowed extensions: {ALLOWED_EXTENSIONS}")
    print("="*50 + "\n")
    
    # Run with threading enabled for better performance
    app.run(debug=True, threaded=True, host='0.0.0.0', port=5000)