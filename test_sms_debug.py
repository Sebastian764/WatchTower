#!/usr/bin/env python3
"""
Debug script to test SMS functionality using the same Python environment
"""
import os
import subprocess
import sys

def test_sms_script():
    print("SMS Debug Test (Virtual Environment Aware)")
    print("=" * 50)
    
    # Check if sms_notify.py exists
    script_path = 'sms_notify.py'
    if os.path.exists(script_path):
        print(f"✓ SMS script found: {script_path}")
        print(f"  File size: {os.path.getsize(script_path)} bytes")
    else:
        print(f"✗ SMS script NOT found: {script_path}")
        return False
    
    # Show current Python executable (this should be in the virtual environment)
    python_exe = sys.executable
    print(f"✓ Using Python: {python_exe}")
    
    # Test if requests is available in current environment
    try:
        import requests
        print(f"✓ requests available in current environment: {requests.__version__}")
    except ImportError:
        print("✗ requests not available in current environment")
        return False
    
    print("\nTesting SMS script execution with current Python environment...")
    
    try:
        # Run the SMS script with the same Python interpreter
        result = subprocess.run([
            python_exe, script_path,
            '--notify', 'false',  # Don't actually send SMS
            '--message', 'Test message from debug script'
        ], capture_output=True, text=True, timeout=10,
        env=dict(os.environ, PYTHONIOENCODING='utf-8'))
        
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"Output:\n{result.stdout}")
        if result.stderr:
            print(f"Errors:\n{result.stderr}")
            
        if result.returncode == 0:
            print("✓ SMS script runs successfully!")
            return True
        else:
            print("✗ SMS script failed")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ SMS script timed out")
        return False
    except Exception as e:
        print(f"✗ Error running SMS script: {e}")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print("\nChecking dependencies...")
    
    required_packages = ['requests', 'flask', 'opencv-python', 'numpy']
    all_good = True
    
    for package in required_packages:
        try:
            if package == 'opencv-python':
                import cv2
                print(f"✓ {package} available (as cv2)")
            else:
                __import__(package)
                print(f"✓ {package} available")
        except ImportError:
            print(f"✗ {package} missing")
            all_good = False
    
    return all_good

def show_environment_info():
    """Show information about the current environment"""
    print("Environment Information:")
    print("=" * 30)
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Virtual environment: {os.environ.get('VIRTUAL_ENV', 'Not detected')}")
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✓ Running in virtual environment")
    else:
        print("⚠️  Not running in virtual environment")

if __name__ == "__main__":
    print("Starting SMS system debug...\n")
    
    # Show environment info
    show_environment_info()
    print()
    
    # Test dependencies
    deps_ok = check_dependencies()
    
    # Test SMS script
    sms_ok = test_sms_script()
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Dependencies: {'✓ OK' if deps_ok else '✗ MISSING'}")
    print(f"SMS Script:   {'✓ OK' if sms_ok else '✗ FAILED'}")
    
    if deps_ok and sms_ok:
        print("\n🎉 SMS system should work!")
        print("\nTo test with actual SMS (be careful - this will send real SMS):")
        print(f"  {sys.executable} sms_notify.py --notify true --message 'Test alert'")
    else:
        print("\n⚠️  SMS system has issues that need fixing")
        if not deps_ok:
            print("   1. Install missing dependencies:")
            print("      pip install requests flask opencv-python numpy")
        if not sms_ok:
            print("   2. Fix the sms_notify.py script issues above")