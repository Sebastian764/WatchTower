import cv2
import numpy as np
import urllib.request
import os
import time

class YOLODetection:
    ## constructor, default values set to .5 and .4
    ## enables us to do adjust values if we need to later
    def __init__(self, confidence_threshold=0.5, nms_threshold=0.4):
        self.confidence_threshold = confidence_threshold
        self.nms_threshold = nms_threshold
        self.YOLO_setup()
    

    def YOLO_setup():
        files = {
            'yolov4.weights' : 'https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.weights',
            'yolov4.cfg': 'https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4.cfg',
        }