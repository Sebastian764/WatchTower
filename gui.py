from flask import Flask, render_template, Response
import cv2
import threading
import time
import argparse

app = Flask(__name__)

# --- CONFIGURATION (YOUR PART) ---
# Replace with the path to your video file
video_path = 'sample_video.mp4'  
# Open the video file
camera = cv2.VideoCapture(video_path)

# --- SHARED VARIABLES (FOR TEAM INTEGRATION) ---
# Your teammate's YOLO code will update this list with coordinates
# e.g., [[x_min1, y_min1, x_max1, y_max1], [x_min2, y_min2, x_max2, y_max2]]
latest_human_coordinates = []

# Your other teammate's Gemini API code will update this boolean
# True if an incident is detected, False otherwise
incident_detected = False

# --- VIDEO STREAMING AND GUI LOGIC (YOUR PART) ---
def generate_frames():
    """
    This function reads video frames, adds overlays, and yields them as JPEG images.
    """
    while True:
        # Read the video frame
        success, frame = camera.read()
        if not success:
            # If the video ends, loop back to the beginning
            camera.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        else:
            # Add rectangles for detected humans
            if latest_human_coordinates:
                for coords in latest_human_coordinates:
                    (x_min, y_min, x_max, y_max) = coords
                    cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                    cv2.putText(frame, "Human", (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Add a status message based on the boolean from the other teammate
            if incident_detected:
                status_text = "Status: Incident Detected!"
                text_color = (0, 0, 255) # Red
            else:
                status_text = "Status: All Clear"
                text_color = (0, 255, 0) # Green

            # Draw the status message on the frame
            cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, text_color, 2)
            
            # Encode the frame as a JPEG image and yield it
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# --- FLASK ROUTES (YOUR PART) ---
@app.route('/')
def index():
    """
    Renders the main HTML page.
    """
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """
    This route provides the video stream to the HTML page.
    """
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# --- MAIN EXECUTION (YOUR PART) ---
if __name__ == '__main__':
    # This is a placeholder for your teammates' code.
    # In the final project, this will be replaced with their code that updates
    # `latest_human_coordinates` and `incident_detected` based on the video stream.
    print("Running as the GUI component. Waiting for teammates' code to update shared variables.")
    print("Example: To see a change, a teammate would need to set latest_human_coordinates = [[100, 100, 200, 300]] and incident_detected = True")
    
    # Run the Flask app
    parser = argparse.ArgumentParser(description='Run Flask app.')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the web server on.')
    args = parser.parse_args()
    app.run(host='0.0.0.0', port=args.port, debug=True)
