import cv2
import numpy as np
import urllib.request
import os
import time

class YOLODetection:
    """
    A class to handle YOLOv4 object detection, specifically for detecting humans.
    It automatically downloads the required model files if they are not present.
    """
    # constructor, default values set
    def __init__(self, confidence_threshold=0.5, nms_threshold=0.4):
        self.confidence_threshold = confidence_threshold
        self.nms_threshold = nms_threshold
        self.yolo_setup()

    def yolo_setup(self):
        """Downloads YOLOv4 model files and loads the network."""
        files = {
            'yolov4.weights': 'https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.weights',
            'yolov4.cfg': 'https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4.cfg',
            'coco.names': 'https://raw.githubusercontent.com/AlexeyAB/darknet/master/data/coco.names'
        }

        print("Checking for YOLO model files...")
        for filename, url in files.items():
            if not os.path.exists(filename):
                print(f"Downloading {filename}...")
                try:
                    urllib.request.urlretrieve(url, filename)
                    print(f"✓ Downloaded {filename} successfully.")
                except Exception as e:
                    print(f"✗ Error downloading {filename}: {e}")
                    # Exit or handle error appropriately if a file is critical
                    return
        
        # Load class names
        try:
            with open('coco.names', 'r') as f:
                self.classes = [line.strip() for line in f.readlines()]
        except Exception as e:
            print(f"✗ Error loading coco.names: {e}")
            return

        # Load YOLO network
        try:
            self.net = cv2.dnn.readNet('yolov4.weights', 'yolov4.cfg')
            layer_names = self.net.getLayerNames()
            # Note: The way to get output layers can vary between OpenCV versions
            self.output_layers = [layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]
            print("✓ YOLO model loaded successfully.")
        except Exception as e:
            print(f"✗ Error loading YOLO model: {e}")

    def detect_humans(self, frame):
        """Detects humans in an OpenCV frame using YOLO."""
        height, width = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)
        outputs = self.net.forward(self.output_layers)

        boxes, confidences, class_ids = [], [], []

        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                # Check if the detected object is a 'person' and meets the confidence threshold
                if self.classes[class_id] == "person" and confidence > self.confidence_threshold:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        # Apply Non-Max Suppression to eliminate redundant overlapping boxes
        indices = cv2.dnn.NMSBoxes(boxes, confidences, self.confidence_threshold, self.nms_threshold)
        
        final_boxes = []
        if len(indices) > 0:
            for i in indices.flatten():
                final_boxes.append(boxes[i])
        
        return final_boxes
