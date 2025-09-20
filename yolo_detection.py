import cv2
import numpy as np
import urllib.request
import os
import time

class YOLODetection:
    # constructor, default values set to .5 and .4
    # enables us to do adjust values if we need to later
    def __init__(self, confidence_threshold=0.5, nms_threshold=0.4):
        self.confidence_threshold = confidence_threshold
        self.nms_threshold = nms_threshold
        self.YOLO_setup()
    

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
        return result_frame



    def run_detection(self, source=0):
        cap = cv2.VideoCapture(source)

        if not cap.isOpened():
            print(f"Error: Could not open video source {source}")
            return

        # FPS calculation
        prev_time = time.time()
        fps = 0

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("End of video or failed to read frame")
                    break

                # Detect humans
                boxes, confidences = self.detect_humans(frame)
                # Draw detections
                result_frame = self.draw_detections(frame, boxes, confidences)

                # Calculate and display FPS
                curr_time = time.time()
                fps = 1 / (curr_time - prev_time)
                prev_time = curr_time
                cv2.putText(result_frame, f'FPS: {fps:.1f}', (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                # Show frame
                cv2.imshow("YOLO Human Detection", result_frame)

                # Quit on 'q'
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break

        finally:
            cap.release()
            cv2.destroyAllWindows()
