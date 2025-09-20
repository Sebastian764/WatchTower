from yolo_detection import YOLODetection
from config import GEMINI_API_KEY


def main():
    # for testing
    #  VIDEO_FILE_PATH = "path to video" 
    
    # Initialize detector
    detector = YOLODetection(
        confidence_threshold=0.5,
        nms_threshold=0.4,
        gemini_api_key=GEMINI_API_KEY
    )
    # Run detection on video file
    detector.run_detection(source=0, save_video=False)
    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("WatchTower Stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")