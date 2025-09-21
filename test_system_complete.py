#!/usr/bin/env python3
"""
Test script to verify all components of the CCTV monitoring system
"""

import os
import sys

def test_imports():
    """Test if all required modules can be imported"""
    print("\n" + "="*60)
    print("TESTING IMPORTS")
    print("="*60)
    
    errors = []
    
    try:
        import cv2
        print("✅ OpenCV (cv2) imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import cv2: {e}")
        print("   Run: pip install opencv-python")
        errors.append("cv2")
    
    try:
        import numpy as np
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import numpy: {e}")
        print("   Run: pip install numpy")
        errors.append("numpy")
    
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import flask: {e}")
        print("   Run: pip install flask")
        errors.append("flask")
    
    try:
        import google.generativeai as genai
        print("✅ Google Generative AI imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import google.generativeai: {e}")
        print("   Run: pip install google-generativeai")
        errors.append("google-generativeai")
    
    return len(errors) == 0

def test_config():
    """Test configuration settings"""
    print("\n" + "="*60)
    print("TESTING CONFIGURATION")
    print("="*60)
    
    try:
        from config import GEMINI_API_KEY, UPLOAD_FOLDER, ALLOWED_EXTENSIONS
        
        # Check API key
        if GEMINI_API_KEY and "AIza" in GEMINI_API_KEY:
            print(f"✅ Gemini API Key found: {GEMINI_API_KEY[:10]}...")
        else:
            print("❌ Invalid or missing Gemini API Key")
            return False
        
        # Check upload folder
        print(f"✅ Upload folder configured: {UPLOAD_FOLDER}")
        
        # Create upload folder if it doesn't exist
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
            print(f"   Created upload folder: {UPLOAD_FOLDER}")
        else:
            print(f"   Upload folder exists")
        
        # Check allowed extensions
        print(f"✅ Allowed extensions: {ALLOWED_EXTENSIONS}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import config: {e}")
        return False
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_gemini_connection():
    """Test Gemini API connection"""
    print("\n" + "="*60)
    print("TESTING GEMINI API CONNECTION")
    print("="*60)
    
    try:
        import google.generativeai as genai
        from config import GEMINI_API_KEY
        
        genai.configure(api_key=GEMINI_API_KEY)
        print("✅ Gemini API configured")
        
        # Test with a simple prompt
        model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest")
        response = model.generate_content("Reply with 'Connection successful' if you receive this.")
        
        if response and response.text:
            print(f"✅ Gemini API responded: {response.text[:50]}...")
            return True
        else:
            print("❌ No response from Gemini API")
            return False
            
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        return False

def test_yolo():
    """Test YOLO model loading"""
    print("\n" + "="*60)
    print("TESTING YOLO DETECTOR")
    print("="*60)
    
    try:
        from yolo_detector import YOLODetection
        
        print("Initializing YOLO detector (this may take a moment)...")
        yolo = YOLODetection()
        print("✅ YOLO detector initialized successfully")
        
        # Check if model files exist
        files = ['yolov4.weights', 'yolov4.cfg', 'coco.names']
        for file in files:
            if os.path.exists(file):
                size = os.path.getsize(file) / (1024*1024)
                print(f"   ✅ {file}: {size:.2f} MB")
            else:
                print(f"   ❌ {file}: Not found")
        
        return True
        
    except Exception as e:
        print(f"❌ YOLO test failed: {e}")
        return False

def test_flask_endpoints():
    """Test Flask endpoints"""
    print("\n" + "="*60)
    print("TESTING FLASK ENDPOINTS")
    print("="*60)
    
    try:
        from app import app
        
        # Test client
        with app.test_client() as client:
            # Test home page
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Home page (/) accessible")
            else:
                print(f"❌ Home page returned status {response.status_code}")
            
            # Test the test endpoint
            response = client.get('/test')
            if response.status_code == 200:
                print("✅ Test endpoint (/test) accessible")
                print(f"   Response: {response.get_json()}")
            else:
                print(f"❌ Test endpoint returned status {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Flask endpoint test failed: {e}")
        return False

def test_video_processing():
    """Test video processing functions"""
    print("\n" + "="*60)
    print("TESTING VIDEO PROCESSING")
    print("="*60)
    
    try:
        from video_processor import timestamp_to_seconds, format_time, parse_timestamps_from_analysis
        
        # Test timestamp conversion
        test_cases = [
            ("1:30", 90),
            ("0:45", 45),
            ("10:00", 600),
        ]
        
        all_passed = True
        for timestamp, expected in test_cases:
            result = timestamp_to_seconds(timestamp)
            if result == expected:
                print(f"✅ timestamp_to_seconds('{timestamp}') = {result}")
            else:
                print(f"❌ timestamp_to_seconds('{timestamp}') = {result}, expected {expected}")
                all_passed = False
        
        # Test parsing
        sample_analysis = """
        0:15-0:25: Two people engaged in physical altercation
        1:30-1:45: Person pushed another person aggressively
        No other incidents detected.
        """
        
        alerts = parse_timestamps_from_analysis(sample_analysis)
        print(f"\n✅ Parsed {len(alerts)} alerts from sample text")
        for alert in alerts:
            print(f"   - {alert['type']} from {alert['start_time']}s to {alert['end_time']}s")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Video processing test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("CCTV MONITORING SYSTEM - DIAGNOSTIC TEST")
    print("="*60)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Gemini API", test_gemini_connection),
        ("YOLO Detector", test_yolo),
        ("Flask Endpoints", test_flask_endpoints),
        ("Video Processing", test_video_processing),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name:20} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your system should be working.")
        print("\nTo run the app:")
        print("  python app.py")
        print("\nThen open: http://localhost:5000")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("1. Install missing packages:")
        print("   pip install flask opencv-python numpy google-generativeai")
        print("\n2. Check your GEMINI_API_KEY in config.py")
        print("\n3. Make sure all .py files are in the same directory")

if __name__ == "__main__":
    main()