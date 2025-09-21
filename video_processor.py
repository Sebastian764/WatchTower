import cv2
import os
import time
import re
from gemini_analyzer import analyze_video_clip, analyze_full_video_with_timestamps

def format_time(seconds):
    """Converts seconds into a MM:SS formatted string."""
    return time.strftime('%M:%S', time.gmtime(seconds))

def process_video(video_path):
    """
    Original function for splitting video into clips.
    Kept for backwards compatibility.
    """
    print(f"Processing video: {video_path}")
    all_results = []
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video file.")
        return [{"error": "Could not open video file."}]

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        fps = 30  # Fallback FPS

    clip_duration_seconds = 10
    frames_per_clip = int(fps * clip_duration_seconds)
    clip_number = 0
    
    while True:
        frames_for_current_clip = []
        for _ in range(frames_per_clip):
            ret, frame = cap.read()
            if not ret:
                break
            frames_for_current_clip.append(frame)
        
        if not frames_for_current_clip:
            break

        start_time_seconds = clip_number * clip_duration_seconds
        end_time_seconds = start_time_seconds + (len(frames_for_current_clip) / fps)
        timestamp_str = f"{format_time(start_time_seconds)} - {format_time(end_time_seconds)}"

        base_filename = os.path.basename(video_path)
        name, _ = os.path.splitext(base_filename)
        output_dir = os.path.dirname(video_path)
        clip_filename = f"{name}_clip_{clip_number}.mp4"
        clip_path = os.path.join(output_dir, clip_filename)
        
        height, width, _ = frames_for_current_clip[0].shape
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(clip_path, fourcc, fps, (width, height))
        
        for f in frames_for_current_clip:
            out.write(f)
        out.release()
        
        analysis_result = analyze_video_clip(clip_path)

        print("\n" + "="*50)
        print(f"ANALYSIS FOR TIMESTAMP {timestamp_str}:")
        print(analysis_result)
        print("="*50 + "\n")

        all_results.append({
            'timestamp': timestamp_str,
            'analysis': analysis_result
        })
        
        try:
            os.remove(clip_path)
        except OSError as e:
            print(f"Error removing clip {clip_path}: {e}")

        clip_number += 1
        
    cap.release()
    print("Finished processing all video clips.")
    return all_results

def analyze_full_video(video_path):
    """
    Analyzes the full video without splitting and returns timestamps of incidents.
    """
    print(f"\n{'='*60}")
    print(f"FULL VIDEO ANALYSIS STARTED")
    print(f"Video path: {video_path}")
    print(f"{'='*60}\n")
    
    try:
        # Verify file exists
        if not os.path.exists(video_path):
            print(f"ERROR: Video file does not exist at {video_path}")
            return []
        
        # Get video information
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"ERROR: Cannot open video file {video_path}")
            return []
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        cap.release()
        
        print(f"Video Information:")
        print(f"  - FPS: {fps}")
        print(f"  - Frame count: {frame_count}")
        print(f"  - Duration: {duration:.2f} seconds")
        print(f"  - File size: {os.path.getsize(video_path) / (1024*1024):.2f} MB")
        
        if duration == 0:
            print("ERROR: Video has zero duration")
            return []
        
        # Send full video to Gemini for analysis
        print("\nSending video to Gemini API for analysis...")
        analysis_text = analyze_full_video_with_timestamps(video_path, duration)
        
        print(f"\nGemini API Response:")
        print("-" * 40)
        print(analysis_text)
        print("-" * 40)
        
        # Parse the analysis to extract timestamps
        alerts = parse_timestamps_from_analysis(analysis_text)
        
        print(f"\nAnalysis Summary:")
        print(f"  - Total alerts found: {len(alerts)}")
        if alerts:
            for i, alert in enumerate(alerts, 1):
                print(f"  - Alert {i}: {alert['type']} from {alert['start_time']:.1f}s to {alert['end_time']:.1f}s")
        
        return alerts
        
    except Exception as e:
        print(f"\nERROR in analyze_full_video: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def parse_timestamps_from_analysis(analysis_text):
    """
    Parses the Gemini analysis response to extract timestamps and incident types.
    Returns a list of alert objects with start_time, end_time, and type.
    """
    alerts = []
    
    if not analysis_text:
        print("WARNING: Empty analysis text received")
        return []
    
    # Convert to lowercase for easier matching
    analysis_lower = analysis_text.lower()
    
    # Check if no incidents were detected
    if "no violent" in analysis_lower or "no incident" in analysis_lower or "scene appears normal" in analysis_lower:
        print("No violent incidents detected in the video")
        return []
    
    # Pattern to match timestamps in various formats
    timestamp_patterns = [
        r'(\d{1,2}:\d{2})\s*[-–—to]\s*(\d{1,2}:\d{2})',  # "0:15-0:25" or "0:15 to 0:25"
        r'between\s*(\d{1,2}:\d{2})\s*and\s*(\d{1,2}:\d{2})',  # "between 0:15 and 0:25"
        r'from\s*(\d{1,2}:\d{2})\s*to\s*(\d{1,2}:\d{2})',  # "from 0:15 to 0:25"
        r'at\s*(\d{1,2}:\d{2})',  # "at 0:15"
        r'around\s*(\d{1,2}:\d{2})',  # "around 0:15"
        r'(\d{1,2}:\d{2})',  # Just "0:15" anywhere
    ]
    
    # Keywords that indicate violence or incidents
    violence_keywords = [
        'violence', 'violent', 'fight', 'fighting', 'assault', 'attack',
        'altercation', 'aggression', 'aggressive', 'punch', 'kick', 'hit',
        'strike', 'physical confrontation', 'scuffle', 'brawl', 'push',
        'shove', 'conflict', 'combat', 'struggle', 'clash'
    ]
    
    # Split into lines for better parsing
    lines = analysis_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        line_lower = line.lower()
        
        # Check if line contains violence keywords
        contains_violence = any(keyword in line_lower for keyword in violence_keywords)
        
        # Try to extract timestamps from this line
        found_timestamp = False
        
        for pattern in timestamp_patterns:
            matches = re.findall(pattern, line, re.IGNORECASE)
            
            for match in matches:
                if isinstance(match, tuple) and len(match) == 2:
                    # Range of timestamps
                    start_time = timestamp_to_seconds(match[0])
                    end_time = timestamp_to_seconds(match[1])
                    
                    if end_time <= start_time:
                        end_time = start_time + 5  # Default 5-second duration
                    
                    alert_type = "VIOLENCE_DETECTED"
                    if any(word in line_lower for word in ['suspicious', 'unusual', 'concerning']):
                        alert_type = "SUSPICIOUS_BEHAVIOR"
                    
                    alerts.append({
                        'start_time': start_time,
                        'end_time': end_time,
                        'type': alert_type,
                        'description': line.strip()
                    })
                    found_timestamp = True
                    break
                    
                elif isinstance(match, str):
                    # Single timestamp
                    time_point = timestamp_to_seconds(match)
                    
                    # Create a 5-second window around the timestamp
                    alerts.append({
                        'start_time': max(0, time_point - 2),
                        'end_time': time_point + 3,
                        'type': "VIOLENCE_DETECTED",
                        'description': line.strip() if contains_violence else f"Incident at {match}"
                    })
                    found_timestamp = True
                    break
            
            if found_timestamp:
                break
    
    # If violence is mentioned but no specific timestamps found, check for other time references
    if not alerts and any(keyword in analysis_lower for keyword in violence_keywords):
        print("Violence mentioned but no timestamps found. Checking for other time references...")
        
        # Look for references like "beginning", "middle", "end", "early", "late"
        if "beginning" in analysis_lower or "start" in analysis_lower or "early" in analysis_lower:
            alerts.append({
                'start_time': 0,
                'end_time': 10,
                'type': "VIOLENCE_DETECTED",
                'description': "Violence detected at the beginning of the video"
            })
        
        # Look for seconds references
        seconds_pattern = r'(\d+)\s*seconds?\s*(?:in|into|mark)?'
        seconds_matches = re.findall(seconds_pattern, analysis_lower)
        for seconds_str in seconds_matches:
            time_point = int(seconds_str)
            alerts.append({
                'start_time': max(0, time_point - 3),
                'end_time': time_point + 3,
                'type': "VIOLENCE_DETECTED",
                'description': f"Violence detected around {time_point} seconds"
            })
    
    # Remove duplicates and sort by start time
    seen = set()
    unique_alerts = []
    for alert in sorted(alerts, key=lambda x: x['start_time']):
        key = (round(alert['start_time']), round(alert['end_time']))
        if key not in seen:
            seen.add(key)
            unique_alerts.append(alert)
    
    print(f"\nParsing Summary:")
    print(f"  - Lines processed: {len(lines)}")
    print(f"  - Raw alerts found: {len(alerts)}")
    print(f"  - Unique alerts after deduplication: {len(unique_alerts)}")
    
    return unique_alerts

def timestamp_to_seconds(timestamp_str):
    """
    Converts a timestamp string (MM:SS or M:SS) to seconds.
    """
    try:
        parts = timestamp_str.strip().split(':')
        if len(parts) == 2:
            minutes = int(parts[0])
            seconds = int(parts[1])
            return minutes * 60 + seconds
        elif len(parts) == 1:
            return int(parts[0])
        return 0
    except:
        print(f"WARNING: Could not parse timestamp '{timestamp_str}'")
        return 0