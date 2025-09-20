import cv2
import numpy as np
import urllib.request
import os
import time
import google.generativeai as genai
from datetime import datetime
import threading
import queue
import tempfile

class YOLODetection:
    # constructor, default values set to .5 and .4
    # enables us to do adjust values if we need to later
    def __init__(self, confidence_threshold=0.5, nms_threshold=0.4, gemini_api_key=None):
        self.confidence_threshold = confidence_threshold
        self.nms_threshold = nms_threshold
        self.gemini_api_key = gemini_api_key
        self.YOLO_setup()
        self.gemini_setup()
        
        # Video recording variables
        self.is_recording = False
        self.current_recording = None
        self.recording_start_time = None
        self.recording_duration = 5  # 10 seconds
        self.frame_buffer = []
        self.analysis_queue = queue.Queue()
        
        # Start analysis thread
        self.analysis_thread = threading.Thread(target=self.process_analysis_queue, daemon=True)
        self.analysis_thread.start()
    
    def gemini_setup(self):
        """Initialize Gemini API"""
        if not self.gemini_api_key:
            print("⚠️ Warning: No Gemini API key provided. Crime detection will be disabled.")
            self.gemini_model = None
            return
            
        try:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
            print("✓ Gemini model initialized successfully")
        except Exception as e:
            print(f"✗ Error initializing Gemini: {e}")
            self.gemini_model = None

    def YOLO_setup(self):
        files = {
            'yolov4.weights' : 'https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.weights',
            'yolov4.cfg': 'https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4.cfg',
        }

        for filename, url in files.items():
            if not os.path.exists(filename):
                try:
                    urllib.request.urlretrieve(url, filename)
                except Exception as e:
                    print(f"✗ Error downloading {filename}: {e}")
                

        # load YOLO network  
        try:
            self.net = cv2.dnn.readNet('yolov4.weights', 'yolov4.cfg')
            layer_names = self.net.getLayerNames()
            self.output_layers = [layer_names[i -1] for i in self.net.getUnconnectedOutLayers()]
        except Exception as e:
            print(f"✗ Error loading YOLO model: {e}")

    #Detect humans in openCV frame using YOLO
    def detect_humans(self, frame):
        height, width = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416,416), (0,0,0), swapRB=True, crop=False)
        self.net.setInput(blob)
        outputs = self.net.forward(self.output_layers)

        boxes, confidences = [], []

        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if class_id == 0 and confidence > self.confidence_threshold:
                    cx = int(detection[0]*width)
                    cy = int(detection[1]*height)
                    w = int(detection[2]*width)
                    h = int(detection[3]*height)
                    x = max(0, cx - w//2)
                    y = max(0, cy - h//2)
                    w = min(w, width - x)
                    h = min(h, height - y)
                    boxes.append([x,y,w,h])
                    confidences.append(float(confidence))

        if len(boxes) > 0:
            indices = cv2.dnn.NMSBoxes(boxes, confidences, self.confidence_threshold, self.nms_threshold)
            if len(indices) > 0:
                final_boxes = [boxes[i] for i in indices.flatten()]
                final_confidences = [confidences[i] for i in indices.flatten()]
                return final_boxes, final_confidences
        return [], []
    
    # record for gemini API
    def start_recording(self, cap):
        if self.is_recording:
            return  # Already recording
            
        self.is_recording = True
        self.recording_start_time = time.time()
        self.frame_buffer = []
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        if fps == 0:
            fps = 30
            
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Create temporary file for recording
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_file.close()
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.current_recording = cv2.VideoWriter(temp_file.name, fourcc, fps, (width, height))
        self.temp_video_path = temp_file.name
        

    def update_recording(self, frame):
        if not self.is_recording or not self.current_recording:
            return
            
        # Write frame to video
        self.current_recording.write(frame)
        
        # Check if 10 seconds have passed
        if time.time() - self.recording_start_time >= self.recording_duration:
            self.stop_recording()

    #stop recording
    def stop_recording(self):
        if not self.is_recording:
            return
            
        self.is_recording = False
        if self.current_recording:
            self.current_recording.release()
            self.current_recording = None
            
            # Queue the video for analysis
            self.analysis_queue.put(self.temp_video_path)

    #gemini ai to analyze
    def analyze_video_with_gemini(self, video_path):
        if not self.gemini_model:
            print("⚠️ Gemini not available for analysis")
            return
            
        try:
            # Upload video to Gemini
            video_file = genai.upload_file(path=video_path)
            # Wait for video to be processed
            while video_file.state.name == "PROCESSING":
                time.sleep(2)
                video_file = genai.get_file(video_file.name)
                
            if video_file.state.name == "FAILED":
                print("✗ Video processing failed")
                return
                
            # Create prompt for crime detection
            prompt = """
            Analyze this video clip carefully and determine if any criminal or suspicious activities are taking place. 
            
            Respond with:
            1. ALERT LEVEL: (LOW/MEDIUM/HIGH/CRITICAL)
            2. DETECTED ACTIVITIES: Brief description of what you observed (bullet points)
            3. CONFIDENCE: Your confidence level in the assessment (1-10)

            If the alert level is MEDIUM or higher, add 🚨 at the start and end of line 1 

            """
            
            # Generate analysis
            response = self.gemini_model.generate_content([video_file, prompt])
            response_text = response.text.strip()
            
            if response_text and len(response_text) > 1:
                print(f"\n{'='*50}")
                print(f"WATCHTOWER ANALYSIS REPORT")
                print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'='*50}")
                print(response_text)
                print(f"{'='*50}\n")
            
            # Clean up the uploaded file
            genai.delete_file(video_file.name)
            
        except Exception as e:
            print(f"✗ Error analyzing video with Gemini: {e}")
        finally:
            # Clean up local temp file
            try:
                os.unlink(video_path)
            except:
                pass

    def process_analysis_queue(self):
        """Process videos in the analysis queue (runs in separate thread)"""
        while True:
            try:
                video_path = self.analysis_queue.get(timeout=1)
                self.analyze_video_with_gemini(video_path)
                self.analysis_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in analysis thread: {e}")

    #draw a box around detection
    def draw_detections(self, frame, boxes, confidences):
        result_frame = frame.copy()

        for box, confidence in zip(boxes, confidences):
            x, y, w, h = box

            #high confidence (green)
            if confidence > .8:
                color = (0, 255, 0)
            elif confidence > .6:
                color = (0, 255, 255)
            else: 
                color = (0, 165, 255)
            
            label = f'Human: {confidence:.2f}' 
            #draw the box
            cv2.rectangle(result_frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(result_frame, label, (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 2)
        
        # Add recording indicator
        if self.is_recording:
            recording_time = time.time() - self.recording_start_time
            remaining_time = max(0, self.recording_duration - recording_time)
            cv2.circle(result_frame, (30, 60), 10, (0, 0, 255), -1)  # Red circle
            cv2.putText(result_frame, f'REC {remaining_time:.1f}s', (50, 65), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        return result_frame

    def run_detection(self, source=0, save_video=False):
        cap = cv2.VideoCapture(source)

        if not cap.isOpened():
            print(f"Error: Could not open video source {source}")
            return
        
        #video properties 
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        if fps == 0:
            fps = 30  # fallback
            
        #setup video writer if saving video
        if save_video:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            output_filename = f"output_{int(time.time())}.mp4"
            out = cv2.VideoWriter(output_filename, fourcc, fps, (width, height))
        
        # FPS calculation
        prev_time = time.time()
        last_detection_time = 0
        detection_cooldown = 2 # Wait 15 seconds before starting new recording after previous one ends

        try:
            print("🎯 Starting human detection with crime analysis...")
            print("Press 'q' to quit")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("End of video or failed to read frame")
                    break

                # Detect humans
                boxes, confidences = self.detect_humans(frame)
                
                # If humans detected and not currently recording and cooldown has passed
                current_time = time.time()
                if (len(boxes) > 0 and 
                    not self.is_recording and 
                    current_time - last_detection_time > detection_cooldown):
                    
                    self.start_recording(cap)
                    last_detection_time = current_time
                
                # Update recording if active
                if self.is_recording:
                    self.update_recording(frame)
                
                # Draw detections
                result_frame = self.draw_detections(frame, boxes, confidences)

                # Calculate and display FPS
                curr_time = time.time()
                fps_current = 1 / (curr_time - prev_time)
                prev_time = curr_time
                cv2.putText(result_frame, f'FPS: {fps_current:.1f}', (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Add status info
                status_color = (0, 255, 0) if self.gemini_model else (0, 0, 255)
                gemini_status = "ONLINE" if self.gemini_model else "OFFLINE"
                cv2.putText(result_frame, f'Gemini: {gemini_status}', (10, height-20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)

                # Show frame
                cv2.imshow("YOLO Human Detection + Crime Analysis", result_frame)

                #save frame to output video
                if save_video:
                    out.write(result_frame)

                # Quit on 'q'
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break

        finally:
            # Stop any ongoing recording
            if self.is_recording:
                self.stop_recording()
                
            cap.release()
            if save_video:
                out.release()
                print(f"Output video saved to: {output_filename}")
            cv2.destroyAllWindows()
            
            # Wait for any remaining analysis to complete
            print("Waiting for analysis to complete...")
            self.analysis_queue.join()
