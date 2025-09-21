#!/usr/bin/env python
"""
Firebase SMS Notification Program - Sends SMS via Firebase Function
Usage: python sms_notify.py --notify true
       python sms_notify.py --notify false
"""

import argparse
import sys
import json
import requests
from datetime import datetime

# Firebase Configuration
FIREBASE_PROJECT_ID = "sms-notifs-403f7"  #  Firebase project ID
FIREBASE_FUNCTION_URL = f"https://us-central1-{FIREBASE_PROJECT_ID}.cloudfunctions.net/sendSMS"

#  Configuration 
YOUR_PHONE_NUMBER = "2676371784"  
CARRIER = "att"  #  att, tmobile, verizon, sprint

# Email-to-SMS Gateway mappings
SMS_GATEWAYS = {
    "att": "txt.att.net",
    "tmobile": "tmomail.net", 
    "verizon": "vtext.com",
    "sprint": "messaging.sprintpcs.com"
}

def send_sms_via_firebase(message, phone_number, carrier):
    
    if carrier not in SMS_GATEWAYS:
        print(f"ERROR: Unsupported carrier '{carrier}'")
        print(f"Supported carriers: {list(SMS_GATEWAYS.keys())}")
        return False
        
    sms_email = "momreznemeri@gmail.com"
    
    payload = {
        "to": sms_email,
        "subject": "Alert",
        "message": message
    }
    
    print(f"Calling Firebase function: {FIREBASE_FUNCTION_URL}")
    print(f"Sending to: {sms_email}")
    
    try:
        response = requests.post(
            FIREBASE_FUNCTION_URL,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"SMS sent successfully via {carrier.upper()}!")
            try:
                result = response.json()
                print(f"Firebase response: {result}")
            except:
                print(f"Firebase response: {response.text}")
            return True
        else:
            print(f" Failed to send SMS. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(" Connection error - check your internet connection")
        return False
    except requests.exceptions.Timeout:
        print(" Timeout error - Firebase function took too long to respond")
        return False
    except requests.exceptions.RequestException as e:
        print(f" Error calling Firebase function: {e}")
        return False

def send_notification(event_message, should_notify):
    if not should_notify:
        print("🔕 Notification flag is FALSE - no SMS sent")
        return
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Prepare SMS message (keep it concise for SMS)
    sms_message = f"{event_message}\nTime: {timestamp}"

    
    print(f"📱 Sending SMS notification...")
    print(f"Message: {event_message}")
    
    # Send SMS via Firebase
    success = send_sms_via_firebase(sms_message, YOUR_PHONE_NUMBER, CARRIER)
    
    if success:
        print(" Notification sent successfully!")
    else:
        print(" Failed to send notification")

def main():
    parser = argparse.ArgumentParser(description='Send SMS notifications via Firebase')
    parser.add_argument('--notify', type=str, choices=['true', 'false'], 
                       required=True, help='Whether to send SMS notification')
    parser.add_argument('--message', type=str, 
                       default='System event occurred', 
                       help='Custom message to send')
    
    args = parser.parse_args()
    
    # Convert string to boolean
    should_notify = args.notify.lower() == 'true'
    
    # Validate configuration
    if YOUR_PHONE_NUMBER == "5551234567":
        print("  WARNING: Please update YOUR_PHONE_NUMBER with your actual phone number")
        print("   Edit the script and change YOUR_PHONE_NUMBER = '5551234567' to your number")
        sys.exit(1)
    
    if CARRIER not in SMS_GATEWAYS:
        print(f"  ERROR: Unsupported carrier '{CARRIER}'")
        print(f"   Supported carriers: {list(SMS_GATEWAYS.keys())}")
        print("   Edit the script and update the CARRIER variable")
        sys.exit(1)
    
    print(f" Firebase SMS Notification System")
    print(f" Phone: {YOUR_PHONE_NUMBER}")
    print(f" Carrier: {CARRIER.upper()} ({SMS_GATEWAYS[CARRIER]})")
    print(f" Firebase Project: {FIREBASE_PROJECT_ID}")
    print("-" * 50)
    
    # Send notification
    send_notification(args.message, should_notify)

if __name__ == "__main__":
    main()